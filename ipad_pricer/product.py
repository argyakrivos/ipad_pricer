import re


class Product:
    def __init__(self, title, size, capacity, connectivity, colour, price, source):
        self.title = title
        self.size = size
        self.capacity = capacity
        self.connectivity = connectivity
        self.colour = colour
        self.price = price
        self.source = source

    def __repr__(self):
        return f"Product(title={self.title}, size={self.size}, capacity={self.capacity}, connectivity={self.connectivity}, colour={self.colour}, price={self.price}, source={self.source})"

    def __str__(self):
        return f"Product: {self.title}, Size: {self.size}, Capacity: {self.capacity}, Connectivity: {self.connectivity}, Colour: {self.colour}, Price: {self.price}, Source: {self.source}"

    @staticmethod
    def from_title(title, price, source):
        capacity_pattern = re.compile(r"(\d+(?:GB|TB))")
        colour_pattern = re.compile(
            r"\b(Purple|Silver|Space Gray|Gold|Blue|Green|Red|Pink|Starlight)\b",
            re.IGNORECASE,
        )

        capacity_match = capacity_pattern.search(title)
        colour_match = colour_pattern.search(title)

        if "11" in title:
            size = "11"
        elif "13" in title:
            size = "13"
        else:
            size = "Unknown"

        if re.search(r"\b(Cellular|5G)\b", title, re.IGNORECASE):
            connectivity = "5G"
        elif re.search(r"\b(WiFi|Wi-Fi)\b", title, re.IGNORECASE):
            connectivity = "Wi-Fi"
        else:
            connectivity = "Unknown"

        capacity = capacity_match.group(0) if capacity_match else "Unknown"
        colour = colour_match.group(0) if colour_match else "Unknown"
        title = f"Apple iPad Air {size}-inch {capacity} {connectivity} {colour}"

        return Product(title, size, capacity, connectivity, colour, price, source)

    def get_capacity_value(self):
        match = re.match(r"(\d+)(GB|TB)", self.capacity, re.IGNORECASE)
        if match:
            value, unit = match.groups()
            value = int(value)
            if unit.lower() == "tb":
                value *= 1024  # Convert TB to GB
            return value
        return 0  # Default value for unknown capacity
