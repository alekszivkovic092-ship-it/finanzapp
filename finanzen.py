import streamlit as st
import pandas as pd
import gspread

# 1. Verbindungsdaten aus den Streamlit Secrets laden
creds_dict = dict(st.secrets["gcp_service_account"])

# KORREKTUR: Die falschen Text-Umbrüche in echte Zeilenumbrüche umwandeln
creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

# 2. Bei Google anmelden (Diese Verbindung gilt für das gesamte Skript)
gc = gspread.service_account_from_dict(creds_dict)

# 3. Funktion zum Laden der Daten
def lade_daten():
    sh = gc.open("Familien Finanzen Datenbank").sheet1
    data = sh.get_all_records()
    return pd.DataFrame(data)

st.title("Unsere Haushaltsfinanzen")

# --- ERWEITERTES FORMULAR ---
with st.form("ausgabe_form"):
    col1, col2 = st.columns(2)
    with col1:
        datum = st.date_input("Datum")
        wer = st.selectbox("Wer?", ["Aleksandar", "Marija"])
        typ = st.selectbox("Typ", ["Ausgabe", "Einnahme"])
    with col2:
        konto = st.selectbox("Konto", ["Bar", "Bank", "Kreditkarte"])
        kategorie = st.selectbox("Kategorie", ["Lebensmittel", "Miete", "Freizeit", "Gehalt", "Sonstiges"])
        betrag = st.number_input("Betrag", min_value=0.0, format="%.2f")
    notiz = st.text_input("Notiz")
    submit = st.form_submit_button("Eintragen")

if submit:
    # KORREKTUR: Der lokale PC-Pfad wurde gelöscht. Wir nutzen die sichere Verbindung von oben.
    sh = gc.open("Familien Finanzen Datenbank").sheet1
    sh.append_row([str(datum), wer, konto, kategorie, typ, betrag, notiz])
    st.success("Erfolgreich gespeichert!")
    st.rerun()

# --- ANALYSE UND LISTE ---
st.divider()
try:
    df = lade_daten()
    if not df.empty:
        # Berechnung Einnahmen/Ausgaben
        einnahmen = df[df['Typ'] == 'Einnahme']['Betrag'].sum()
        ausgaben = df[df['Typ'] == 'Ausgabe']['Betrag'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Gesamt Einnahmen", f"{einnahmen:.2f} €")
        col2.metric("Gesamt Ausgaben", f"{ausgaben:.2f} €")
        col3.metric("Bilanz", f"{(einnahmen - ausgaben):.2f} €")
        
        st.subheader("Bisherige Buchungen")
        st.dataframe(df)
    else:
        st.warning("Tabelle ist leer.")
except Exception as e:
    st.error(f"Fehler beim Laden: {e}")

# --- LÖSCHEN ---
st.subheader("Eintrag löschen")
zeilennummer = st.number_input("Zeilennummer:", min_value=2, step=1)
if st.button("Löschen"):
    # KORREKTUR: Auch hier wurde der PC-Pfad entfernt.
    sh = gc.open("Familien Finanzen Datenbank").sheet1
    sh.delete_rows(int(zeilennummer))
    st.rerun()
