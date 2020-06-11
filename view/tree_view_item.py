BOOLEAN_TO_STRING_DICT = {
    True: 'yes',
    False: 'no',
    None: ''
}


def get_count(self):
    return self.count if self.count is not None else ''


def get_symmetry_breaking(self):
    return BOOLEAN_TO_STRING_DICT[self.symmetry_breaking]

# TODO: zamiast tego lambdy!!!