from django.db import models

regulations = "https://drive.google.com/file/d/1ZpVOlsm9EvjMCfV0xy3tbckCbaJ33lFd/view?usp=drive_link"
informed_consent = "https://drive.google.com/file/d/1ZpVOlsm9EvjMCfV0xy3tbckCbaJ33lFd/view?usp=drive_link"

class Ranges(models.TextChoices):
    K10 = '10k', 'Beginner'
    K9 = '9k', '9th kyu'
    K8 = '8k', '8th kyu'
    K7 = '7k', '7th kyu'
    K6 = '6k', '6th kyu'
    K5 = '5k', '5th kyu'
    K4 = '4k', '4th kyu'
    K3 = '3k', '3rd kyu'
    K2 = '2k', '2nd kyu'
    K1 = '1k', '1st kyu'
    D1 = '1d', '1st Dan'
    D2 = '2d', '2nd Dan'
    D3 = '3d', '3rd Dan'
    D4 = '4d', '4th Dan'
    D5 = '5d', '5th Dan'
    D6 = '6d', '6th Dan'
    D7 = '7d', '7th Dan'
    D8 = '8d', '8th Dan'
    D9 = '9d', '9th Dan'
    D10 = '10d', '10th Dan'

    @property
    def belt_color(self):
        colors = {
            '10k': '#FFFFFF', # 'White'
            '9k': '#FFFF00', # 'Yellow stripe'
            '8k': '#FFFF00', # 'Yellow'
            '7k': '#FFA500', # 'Orange'
            '6k': '#008000', # 'Green'
            '5k': '#7700FF', # 'Violet'
            '4k': '#7700FF', # 'Violet'
            '3k': '#773333', # 'Brown'
            '2k': '#773333', # 'Brown'
            '1k': '#773333', # 'Brown'
            '1d': '#000000', # 'Black'
            '2d': '#000000', # 'Black'
            '3d': '#000000', # 'Black'
            '4d': '#000000', # 'Black'
            '5d': '#000000', # 'Black'
            '6d': '#000000', # 'Black'
            '7d': '#000000', # 'Black'
            '8d': '#000000', # 'Black'
            '9d': '#000000', # 'Black'
            '10d': '#000000', # 'Black'
        }
        return colors.get(self.value, '')
