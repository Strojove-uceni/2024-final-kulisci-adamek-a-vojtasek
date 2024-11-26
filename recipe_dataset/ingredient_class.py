import re

class Ingredient:
    def __init__(self, raw_text):
        self.raw_text = raw_text.lower()  # Store original input
        self.quantity = None
        self.units = None
        self.base = None
        self.style = None
        self.adjectives = []

    def parse_quantity(self):
        """Extract quantity from the raw text."""
        match = re.match(r"^[\d/]+", self.raw_text)
        self.quantity = match.group(0) if match else None
        return self.quantity

    def parse_units(self, units):
        """Extract units from the raw text."""
        pattern = r'\b(' + '|'.join(f"{unit}s?" for unit in units) + r')\b'
        match = re.search(pattern, self.raw_text)
        self.units = match.group(0) if match else None
        return self.units

    def parse_style(self, styles):
        """Extract styles (e.g., 'chopped', 'diced') from the raw text."""
        pattern = r'\b(' + '|'.join([f"{style}( and \w+)?" for style in styles]) + r')\b'
        match = re.search(pattern, self.raw_text)
        self.style = match.group(0) if match else None
        return self.style

    def parse_adjectives(self, adjectives):
        """Extract adjectives from the raw text."""
        pattern = r'\b(' + '|'.join(adjectives) + r')\b'
        matches = re.findall(pattern, self.raw_text)
        self.adjectives = matches
        return self.adjectives

    def clean_base(self):
        """Clean the base ingredient by removing quantity, units, styles, and adjectives."""
        base = self.raw_text
        if self.quantity:
            base = base.replace(self.quantity, "").strip()
        if self.units:
            base = base.replace(self.units, "").strip()
        if self.style:
            base = base.replace(self.style, "").strip()
        for adj in self.adjectives:
            base = base.replace(adj, "").strip()
        # Remove trailing phrases like 'to taste' or alternatives
        base = re.sub(r'\b(to taste|or .+|,\s*and.+|,.*)$', '', base).strip()
        self.base = base
        return self.base

    def parse_all(self, units, styles, adjectives):
        """Run all parsing methods in order."""
        self.parse_quantity()
        self.parse_units(units)
        self.parse_style(styles)
        self.parse_adjectives(adjectives)
        self.clean_base()

    def __repr__(self):
        return (f"Ingredient(base='{self.base}', quantity='{self.quantity}', units='{self.units}', "
                f"style='{self.style}', adjectives={self.adjectives})")