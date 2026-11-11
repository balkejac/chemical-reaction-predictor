from drafter import *
from dataclasses import dataclass


# ------------------------------------------------------------
# DATA CLASSES
# ------------------------------------------------------------

@dataclass
class ReactionResult:
    """Stores the results of one supported chemical reaction."""
    reactant_1: str
    reactant_2: str
    amount_1: float
    amount_2: float
    balanced_equation: str
    products: list[str]
    reaction_type: str
    limiting_reactant: str
    theoretical_yield: float
    remaining_reactants: list[str]
    heat_released: float | None


@dataclass
class State:
    """Stores information that needs to be available throughout the website."""
    reactant_1: str
    reactant_2: str
    amount_1: float
    amount_2: float
    reaction_type: str
    current_result: ReactionResult | None
    reaction_history: list[ReactionResult]
    error_message: str


# ------------------------------------------------------------
# SUPPORTED REACTION DATABASE
# The heat value is the enthalpy change (kJ) for the balanced
# reaction exactly as written. None means a value is not supplied.
# ------------------------------------------------------------

REACTIONS = [
    {
        "type": "Acid-base",
        "reactants": ["HCl", "NaOH"],
        "reactant_coefficients": [1, 1],
        "products": ["NaCl", "H2O"],
        "product_coefficients": [1, 1],
        "molar_masses": {
            "HCl": 36.46,
            "NaOH": 40.00,
            "NaCl": 58.44,
            "H2O": 18.015
        },
        "equation": "HCl + NaOH -> NaCl + H2O",
        "delta_h": -57.3
    },
    {
        "type": "Precipitation",
        "reactants": ["BaCl2", "Na2SO4"],
        "reactant_coefficients": [1, 1],
        "products": ["BaSO4", "NaCl"],
        "product_coefficients": [1, 2],
        "molar_masses": {
            "BaCl2": 208.23,
            "Na2SO4": 142.04,
            "BaSO4": 233.39,
            "NaCl": 58.44
        },
        "equation": "BaCl2 + Na2SO4 -> BaSO4 + 2NaCl",
        "delta_h": None
    },
    {
        "type": "Single replacement",
        "reactants": ["Zn", "CuSO4"],
        "reactant_coefficients": [1, 1],
        "products": ["ZnSO4", "Cu"],
        "product_coefficients": [1, 1],
        "molar_masses": {
            "Zn": 65.38,
            "CuSO4": 159.61,
            "ZnSO4": 161.44,
            "Cu": 63.546
        },
        "equation": "Zn + CuSO4 -> ZnSO4 + Cu",
        "delta_h": None
    },
    {
        "type": "Combustion",
        "reactants": ["CH4", "O2"],
        "reactant_coefficients": [1, 2],
        "products": ["CO2", "H2O"],
        "product_coefficients": [1, 2],
        "molar_masses": {
            "CH4": 16.043,
            "O2": 31.998,
            "CO2": 44.01,
            "H2O": 18.015
        },
        "equation": "CH4 + 2O2 -> CO2 + 2H2O",
        "delta_h": -890.3
    }
]

REACTION_TYPES = [
    "Acid-base",
    "Precipitation",
    "Single replacement",
    "Combustion"
]


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def find_reaction(reactant_1: str, reactant_2: str, reaction_type: str):
    """Finds a supported reaction, allowing the reactants in either order."""
    first = reactant_1.strip()
    second = reactant_2.strip()

    for reaction in REACTIONS:
        if reaction["type"] == reaction_type:
            expected = reaction["reactants"]
            if first == expected[0] and second == expected[1]:
                return reaction, False
            if first == expected[1] and second == expected[0]:
                return reaction, True

    return None, False


def calculate_reaction_result(reactant_1: str, reactant_2: str,
                              amount_1: float, amount_2: float,
                              reaction_type: str) -> ReactionResult | None:
    """Calculates limiting reactant, theoretical yield, and available heat."""
    reaction, reversed_order = find_reaction(
        reactant_1, reactant_2, reaction_type
    )

    if reaction is None:
        return None

    # Put the amounts in the same order as the reaction database.
    if reversed_order:
        amount_1, amount_2 = amount_2, amount_1
        reactant_1, reactant_2 = reactant_2, reactant_1

    coefficients = reaction["reactant_coefficients"]
    products = reaction["products"]
    product_coefficients = reaction["product_coefficients"]

    # The reaction extent is determined by whichever reactant runs out first.
    possible_reaction_1 = amount_1 / coefficients[0]
    possible_reaction_2 = amount_2 / coefficients[1]
    reaction_extent = min(possible_reaction_1, possible_reaction_2)

    if abs(possible_reaction_1 - possible_reaction_2) < 0.0000001:
        limiting_reactant = "Neither; the reactants are in the exact mole ratio"
    elif possible_reaction_1 < possible_reaction_2:
        limiting_reactant = reactant_1
    else:
        limiting_reactant = reactant_2

    # Calculate how much of each reactant remains after the reaction.
    remaining_1 = amount_1 - reaction_extent * coefficients[0]
    remaining_2 = amount_2 - reaction_extent * coefficients[1]
    remaining_reactants = [
        reactant_1 + ": " + format(max(0, remaining_1), ".4f") + " mol remaining",
        reactant_2 + ": " + format(max(0, remaining_2), ".4f") + " mol remaining"
    ]

    # Calculate the theoretical amount of each product in moles.
    product_amounts = []
    for index in range(len(products)):
        product_moles = reaction_extent * product_coefficients[index]
        product_amounts.append(product_moles)

    # The first product is used as the main theoretical-yield value.
    theoretical_yield = product_amounts[0]

    # Include the predicted amount of every product in the displayed list.
    product_descriptions = []
    for index in range(len(products)):
        description = products[index] + ": " + format(product_amounts[index], ".4f") + " mol"
        product_descriptions.append(description)

    # A negative enthalpy change means heat is released.
    if reaction["delta_h"] is None:
        heat_released = None
    else:
        heat_released = -reaction["delta_h"] * reaction_extent

    return ReactionResult(
        reactant_1,
        reactant_2,
        amount_1,
        amount_2,
        reaction["equation"],
        product_descriptions,
        reaction_type,
        limiting_reactant,
        theoretical_yield,
        remaining_reactants,
        heat_released
    )


def navigation_buttons():
    """Creates the navigation buttons used on each page."""
    return [
        Button("Home", "index"),
        Button("Enter a Reaction", "input_page"),
        Button("Reaction History", "history_page"),
        Button("Learn About Reactions", "learn_page")
    ]


def result_content(result: ReactionResult):
    """Creates the content shared by the results and detail pages."""
    content = [
        Header("Reaction Results"),
        "Reactants: " + result.reactant_1 + " and " + result.reactant_2,
        "Starting amounts: " + format(result.amount_1, ".4f") + " mol of "
        + result.reactant_1 + " and " + format(result.amount_2, ".4f")
        + " mol of " + result.reactant_2,
        "Reaction type: " + result.reaction_type,
        "Balanced equation: " + result.balanced_equation,
        "Predicted products:"
    ]

    for product in result.products:
        content.append("- " + product)

    content.append("Limiting reactant: " + result.limiting_reactant)
    content.append(
        "Theoretical yield of " + result.products[0].split(":")[0]
        + ": " + format(result.theoretical_yield, ".4f") + " mol"
    )
    content.append("Remaining reactants:")
    for reactant in result.remaining_reactants:
        content.append("- " + reactant)

    if result.heat_released is None:
        content.append("Heat information: Not available in this program's reaction database.")
    elif result.heat_released >= 0:
        content.append("Heat released: " + format(result.heat_released, ".2f") + " kJ")
    else:
        content.append("Heat absorbed: " + format(abs(result.heat_released), ".2f") + " kJ")

    content.append(
        "Note: These are theoretical calculations for supported reactions. "
        "They do not replace lab instructions or safety procedures."
    )
    return content


# ------------------------------------------------------------
# ROUTE 1: HOME PAGE
# ------------------------------------------------------------

@route
def index(state: State) -> Page:
    content = [
        Header("Chemistry Reaction Predictor"),
        "Explore what may happen when two supported reactants are combined.",
        "Enter reactants and their amounts in moles to see a balanced equation, "
        "reaction type, limiting reactant, and theoretical product yield.",
        "This student tool currently supports four reaction examples."
    ]
    content.extend(navigation_buttons())
    return Page(state, content)


# ------------------------------------------------------------
# ROUTE 2: INPUT PAGE
# ------------------------------------------------------------

@route
def input_page(state: State) -> Page:
    content = [
        Header("Enter Your Reactants"),
        "Enter the chemical formulas exactly as shown in the Learn page.",
        "First reactant formula:",
        TextBox("reactant_1", state.reactant_1),
        "First reactant amount (moles):",
        TextBox("amount_1", state.amount_1, kind="number"),
        "Second reactant formula:",
        TextBox("reactant_2", state.reactant_2),
        "Second reactant amount (moles):",
        TextBox("amount_2", state.amount_2, kind="number"),
        "Reaction category:",
        SelectBox("reaction_type", REACTION_TYPES, state.reaction_type),
        Button("Predict Reaction", "calculate_reaction")
    ]

    if state.error_message != "":
        content.append("Error: " + state.error_message)

    content.extend(navigation_buttons())
    return Page(state, content)


# ------------------------------------------------------------
# ROUTE 3: CALCULATE REACTION
# ------------------------------------------------------------

@route
def calculate_reaction(state: State, reactant_1: str, amount_1: float,
                         reactant_2: str, amount_2: float,
                         reaction_type: str) -> Page:
    state.reactant_1 = reactant_1.strip()
    state.reactant_2 = reactant_2.strip()
    state.amount_1 = amount_1
    state.amount_2 = amount_2
    state.reaction_type = reaction_type
    state.error_message = ""

    # Conditional 1: Check for blank reactant fields.
    if state.reactant_1 == "" or state.reactant_2 == "":
        state.error_message = "Please enter both reactant formulas."
        return input_page(state)

    # Conditional 2: Check that both amounts are greater than zero.
    if state.amount_1 <= 0 or state.amount_2 <= 0:
        state.error_message = "Both reactant amounts must be greater than zero."
        return input_page(state)

    # Conditional 3: Check whether the selected reaction is supported.
    result = calculate_reaction_result(
        state.reactant_1,
        state.reactant_2,
        state.amount_1,
        state.amount_2,
        state.reaction_type
    )

    if result is None:
        state.error_message = (
            "That combination is not in the supported reaction list. "
            "Check the formulas and reaction category on the Learn page."
        )
        return input_page(state)

    # Save the successful result in the current result and history list.
    state.current_result = result
    state.reaction_history.append(result)
    return results_page(state)


# ------------------------------------------------------------
# ROUTE 4: RESULTS PAGE
# ------------------------------------------------------------

@route
def results_page(state: State) -> Page:
    if state.current_result is None:
        return Page(state, [
            Header("No Reaction Yet"),
            "Enter a supported reaction before viewing results.",
            Button("Enter a Reaction", "input_page")
        ])

    content = result_content(state.current_result)
    content.extend(navigation_buttons())
    return Page(state, content)


# ------------------------------------------------------------
# ROUTE 5: HISTORY PAGE
# ------------------------------------------------------------

@route
def history_page(state: State) -> Page:
    content = [Header("Reaction History")]

    if len(state.reaction_history) == 0:
        content.append("You have not calculated any reactions yet.")
    else:
        # This loop displays every saved ReactionResult in the State list.
        for index in range(len(state.reaction_history)):
            result = state.reaction_history[index]
            content.append(
                str(index + 1) + ". " + result.reactant_1 + " + "
                + result.reactant_2 + " | " + result.balanced_equation
            )
            content.append(Button(
                "View Reaction " + str(index + 1),
                "reaction_detail_page",
                [Argument("reaction_index", index)]
            ))

    content.extend(navigation_buttons())
    return Page(state, content)


# ------------------------------------------------------------
# ROUTE 6: REACTION DETAILS PAGE
# ------------------------------------------------------------

@route
def reaction_detail_page(state: State, reaction_index: int) -> Page:
    if reaction_index < 0 or reaction_index >= len(state.reaction_history):
        return Page(state, [
            Header("Reaction Not Found"),
            "That history entry does not exist.",
            Button("Back to History", "history_page")
        ])

    result = state.reaction_history[reaction_index]
    content = result_content(result)
    content.append(Button("Back to History", "history_page"))
    content.extend(navigation_buttons())
    return Page(state, content)


# ------------------------------------------------------------
# ROUTE 7: LEARN PAGE
# ------------------------------------------------------------

@route
def learn_page(state: State) -> Page:
    content = [
        Header("Learn About Supported Reactions"),
        "Use the exact formulas below when entering a reaction.",
        "1. Acid-base neutralization",
        "Reactants: HCl and NaOH",
        "Equation: HCl + NaOH -> NaCl + H2O",
        "An acid and a base react to form a salt and water.",
        "2. Precipitation (double replacement)",
        "Reactants: BaCl2 and Na2SO4",
        "Equation: BaCl2 + Na2SO4 -> BaSO4 + 2NaCl",
        "The reaction forms solid barium sulfate (BaSO4).",
        "3. Single replacement",
        "Reactants: Zn and CuSO4",
        "Equation: Zn + CuSO4 -> ZnSO4 + Cu",
        "Zinc replaces copper in copper(II) sulfate.",
        "4. Combustion",
        "Reactants: CH4 and O2",
        "Equation: CH4 + 2O2 -> CO2 + 2H2O",
        "Methane reacts with oxygen to form carbon dioxide and water.",
        "Amounts must be entered in moles. Reactants may be entered in either order.",
        "Heat values are included only for reactions where this program has a value."
    ]
    content.extend(navigation_buttons())
    return Page(state, content)


# ------------------------------------------------------------
# START THE WEBSITE
# ------------------------------------------------------------

start_server(State(
    "HCl",
    "NaOH",
    1.0,
    1.0,
    "Acid-base",
    None,
    [],
    ""
))
