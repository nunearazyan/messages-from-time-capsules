import folium
from geopy.geocoders import Nominatim
import os
import glob
import xml.etree.ElementTree as ET

# Erstellen des Geolocators, um die Koordinaten der Städte zu ermitteln
geolocator = Nominatim(user_agent="city_locator")

# Funktion zum Erhalten der Koordinaten einer Stadt
def get_coordinates(city_name):
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        return None

# Funktion zum Einlesen und Extrahieren der Metadaten aus XML
def get_metadata(city):
    # Dictionary für die Dateipfade der XML-Dateien
    city_metadata_files = {
        "Nowosibirsk": "72_DS_NOWOSIBIRSK_МН-НВФ-13845.xml",
        "Rostow am Don": "72_DS_ROSTOW_РОМК-КП-27720.xml",
        "Murmansk": "67_HDS_MURMANSK_МОМ-ОФ-24525.xml",
        "Perm": "72_DS_PERM_21683.xml",
        "Sankt Petersburg": "74_HS_SPB.xml"
    }
    
    filename = city_metadata_files.get(city, None)
    if filename:
        xml_path = os.path.join("Metadaten", filename)
        if os.path.exists(xml_path):
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()

                # Namespace für mods
                namespaces = {'mods': 'http://www.loc.gov/mods/v3'}

                # Extrahieren spezifischer Felder aus der XML
                title_rus = root.find(".//mods:title[@lang='rus']", namespaces)
                title_ger = root.find(".//mods:title[@lang='ger']", namespaces)
                date_created = root.find(".//mods:dateCreated[@type='written']", namespaces)
                date_opened = root.find(".//mods:dateCreated[@type='opened']", namespaces)
                institution_rus = root.find(".//mods:namePart[@lang='rus']", namespaces)
                institution_ger = root.find(".//mods:namePart[@lang='ger']", namespaces)

                physical_form = root.find(".//mods:form", namespaces)
                physical_extent = root.find(".//mods:extent", namespaces)
                physical_dimensions = root.find(".//mods:dimensions", namespaces)
                material = root.find(".//mods:material", namespaces)
                notes = root.findall(".//mods:note", namespaces)

                # Erstellen des HTML für die Metadaten
                metadata_html = f"""
                <h4><b>Botschaft aus der Zeitkapsel / Послание из капсулы времени.<br> {city}</b></h4>
                <b>Titel:</b> {title_rus.text if title_rus is not None else "Nicht verfügbar"} / {title_ger.text if title_ger is not None else "Nicht verfügbar"}<br>
                <b>Zeitkapsel eingelegt am:</b> {date_created.text if date_created is not None else "Nicht verfügbar"}<br>
                <b>Zeitkapsel geöffnet am:</b> {date_opened.text if date_opened is not None else "Nicht verfügbar"}<br>
                <b>Aufbewahrende Institution:</b> {institution_rus.text if institution_rus is not None else "Nicht verfügbar"} / {institution_ger.text if institution_ger is not None else "Nicht verfügbar"}<br><br>
                <h5><b>Physische Beschreibung</b></h5>
                <b>Form:</b> {physical_form.text if physical_form is not None else "Nicht verfügbar"}<br>
                <b>Umfang:</b> {physical_extent.text if physical_extent is not None else "Nicht verfügbar"}<br>
                <b>Maße:</b> {physical_dimensions.text if physical_dimensions is not None else "Nicht verfügbar"}<br>
                <b>Material:</b> {material.text if material is not None else "Nicht verfügbar"}<br>
                <b>Anmerkungen:</b> {'; '.join([note.text for note in notes]) if notes else "Keine"}<br><br>
                """
                return metadata_html
            except ET.ParseError as e:
                return f"<p>Fehler beim Parsen der XML-Datei: {e}</p>"
        else:
            return "<p>Metadaten-Datei nicht gefunden.</p>"
    else:
        return "<p>Keine Metadaten verfügbar.</p>"

# Funktion zum Finden von Bildern, Transkriptionen und Übersetzungen
def get_files(city):
    city_patterns = {
        "Nowosibirsk": "*NOWOSIBIRSK*",
        "Rostow am Don": "*ROSTOW*",
        "Murmansk": "*MURMANSK*",
        "Perm": "*PERM*",
        "Sankt Petersburg": "*SPB*"
    }
    
    pattern = city_patterns.get(city, None)
    if not pattern:
        return "<p>Keine Dateien verfügbar.</p>"

    # Findet alle Bilder, Transkriptionen, Übersetzungen und Metadaten für die jeweilige Stadt
    image_files = glob.glob(os.path.join("Digitalisate", f"{pattern}.JPG"))
    transcriptions = glob.glob(os.path.join("Transkribierte Texte", f"{pattern}.txt"))
    translations = glob.glob(os.path.join("Übersetzung", f"{pattern}.txt"))
    metadata_file = glob.glob(os.path.join("Metadaten", f"{pattern}.xml"))

    # Generieren des HTML
    file_html = "<h5><b>Dateien</b></h5>"
    
    if image_files:
        file_html += "<b>Bilder:</b><br>" + "<div style='display: flex; flex-wrap: wrap; gap: 10px;'>" + "".join([
            f"<a href='{f.replace(os.sep, '/')}' target='_blank' title='Datei anzeigen' style='display: inline-block;'><img src='{f.replace(os.sep, '/')}' alt='{os.path.basename(f)}' style='max-width:100px;'></a>"
            for f in image_files
        ]) + "</div><br>"
    
    if transcriptions:
        file_html += "<b>Transkriptionen:</b><br>" + "<br>".join([
            f"<a href='{f.replace(os.sep, '/')}' target='_blank' title='Datei anzeigen'>{os.path.basename(f)}</a>"
            for f in transcriptions
        ]) + "<br>" 
    
    if translations:
        file_html += "<b>Übersetzungen:</b><br>" + "<br>".join([
            f"<a href='{f.replace(os.sep, '/')}' target='_blank' title='Datei anzeigen'>{os.path.basename(f)}</a>"
            for f in translations
        ]) + "<br>" 

    if metadata_file:
        file_html += "<b>Metadaten:</b><br>" + "".join([
            f"<a href='{f.replace(os.sep, '/')}' target='_blank' title='Metadaten anzeigen'>{os.path.basename(f)}</a><br>"
            for f in metadata_file
        ]) + "<br>"  
    
    return file_html

# Liste der Städte und die dazugehörigen Informationen
cities_info = {
    "Sankt Petersburg": "1974",
    "Nowosibirsk": "1972",
    "Rostow am Don": "1972",
    "Murmansk": "1967",
    "Perm": "1972"
}

# Erstellen einer Folium-Karte mit einem zentralen Punkt (ungefährer geografischer Mittelpunkt von der ehemaligen Sowjetunion)
map_center = [60, 90] 
my_map = folium.Map(
    location=map_center, 
    zoom_start=3, 
    tiles='cartodb positron', 
    attr='Map data © OpenStreetMap contributors'
)

# Durch die Städte iterieren und geografische Marker hinzufügen
for city, info in cities_info.items():
    coordinates = get_coordinates(city)
    if coordinates:
        # Metadaten und Dateien für die jeweilige Stadt
        metadata_html = get_metadata(city)
        file_html = get_files(city)

        # Kombinieren der Informationen zu einem HTML-Popup, der erscheint, wenn man über die Stadt hovert
        popup_html = metadata_html + file_html

        # Hinzufügen eines Markers mit Popup
        folium.CircleMarker(
            location=coordinates,
            radius=10,
            color='red',
            weight=8,
            fill=True,
            fill_color='yellow',
            fill_opacity=0.6,
            popup=folium.Popup(popup_html, max_width=600),
            tooltip=folium.Tooltip(f"<span style='font-size: 16px; color: black;'>Klicken für mehr Info</span>")
        ).add_to(my_map)
    else:
        print(f"Koordinaten für {city} konnten nicht gefunden werden.")

# Karte in einer HTML-Datei speichern
script_dir = os.path.dirname(os.path.abspath(__file__))  # Ordner des aktuellen Skripts

# Karte wird in einer HTML-Datei im gleichen Verzeichnis wie das Skript gespeichert
output_file = os.path.join(script_dir, "time_capsules_map.html")
my_map.save(output_file)

print(f"Die Karte wurde erfolgreich erstellt und als '{output_file}' gespeichert.")