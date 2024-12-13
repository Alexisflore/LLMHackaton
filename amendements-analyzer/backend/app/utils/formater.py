import html
from bs4 import BeautifulSoup
from typing import Dict

def clean_text(text: str) -> str:
    """
    To clean HTML formating.
    """
    replacements = {
        "\xa0": " ",
        "\u200b": "",
        "&#x00E9;": "é",
        "&#x2019;": "'",
        "&#x00E0;": "à",
        "&nbsp;": " ",
        "&#39;": "'",
    }
    html_cleaned_text = html.unescape(text)
    cleaned_text = BeautifulSoup(html_cleaned_text, "html.parser").get_text()
    for old, new in replacements.items():
        cleaned_text = cleaned_text.replace(old, new)
    
    return cleaned_text

def extract_relevant_data(row: Dict) -> Dict:
    """
    To extract the relevant data to be embed.
    Args:
        row (str): full row from csv file.
    Returns:
        Dict: relevant data ready to be embed and unique id.
    """
    return {
        "context_legislatif": row["Titre court"],
        "uid": row["uid"],
        "contenu_amendement": row["corps.contenuAuteur.dispositif"],
        "resume_amendement": row["corps.contenuAuteur.exposeSommaire"],
        "article": row["pointeurFragmentTexte.division.titre"],
        "etat": row["cycleDeVie.etatDesTraitements.etat.libelle"],
        "date_depot": row["cycleDeVie.dateDepot"],
        "lien_amendement": row["URL Amendement"],
    }