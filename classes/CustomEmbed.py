import discord.embeds


class CustomEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._fields = None

    def insert_field_in(self, index: int, *, name, value, inline=True):
        """Insert a field to the embed object.

        The index must point to a valid pre-existing field.

        This function returns the class instance to allow for fluent-style
        chaining.

        Parameters
        -----------
        index: int
            The index of the field to insert.
        name: str
            The name of the field.
        value: str
            The value of the field.
        inline: bool
            Whether the field should be displayed inline.

        Raises
        -------
        IndexError
            An invalid index was provided.
        """
        if index > len(self.fields):
            raise IndexError('field index out of range')
        field = {
            'inline': inline,
            'name': str(name),
            'value': str(value)
        }
        self._fields.insert(index, field)
        return self
