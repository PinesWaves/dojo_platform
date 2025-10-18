from django.db import models

regulations = "https://drive.google.com/file/d/1ZpVOlsm9EvjMCfV0xy3tbckCbaJ33lFd/view?usp=drive_link"
informed_consent = "https://drive.google.com/file/d/1ZpVOlsm9EvjMCfV0xy3tbckCbaJ33lFd/view?usp=drive_link"

class Ranges(models.TextChoices):
    K10 = '10k', 'Beginner'  # White
    K9 = '9k', '9th kyu'  # Yellow stripe
    K8 = '8k', '8th kyu'  # Yellow
    K7 = '7k', '7th kyu'  # Orange
    K6 = '6k', '6th kyu'  # Green
    K5 = '5k', '5th kyu'  # Violet
    K4 = '4k', '4th kyu'  # Violet
    K3 = '3k', '3rd kyu'  # Brown
    K2 = '2k', '2nd kyu'  # Brown
    K1 = '1k', '1st kyu'  # Brown
    D1 = '1d', '1st Dan'  # Black
    D2 = '2d', '2nd Dan'  # Black
    D3 = '3d', '3rd Dan'  # Black
    D4 = '4d', '4th Dan'  # Black
    D5 = '5d', '5th Dan'  # Black
    D6 = '6d', '6th Dan'  # Black
    D7 = '7d', '7th Dan'  # Black
    D8 = '8d', '8th Dan'  # Black
    D9 = '9d', '9th Dan'  # Black
    D10 = '10d', '10th Dan'  # Black
