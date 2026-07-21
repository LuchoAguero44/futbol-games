import json
import requests

# Tu lista completa de jugadores
jugadores = [
    "Lionel Messi", "Cristiano Ronaldo", "Diego Maradona", "Pelé", "Zinedine Zidane",
    "Ronaldinho", "Ronaldo Nazário", "Neymar", "Kylian Mbappé", "Erling Haaland",
    "Robert Lewandowski", "Kevin De Bruyne", "Luka Modrić", "Toni Kroos", "Karim Benzema",
    "Sergio Ramos", "Andrés Iniesta", "Xavi Hernández", "Gerard Piqué", "Iker Casillas",
    "Manuel Neuer", "Gianluigi Buffon", "Thibaut Courtois", "Virgil van Dijk", "Mohamed Salah",
    "Sadio Mané", "Harry Kane", "Son Heung-min", "Antoine Griezmann", "Paul Pogba",
    "N'Golo Kanté", "Eden Hazard", "Gareth Bale", "Luis Suárez", "Edinson Cavani",
    "Ángel Di María", "Paulo Dybala", "Lautaro Martínez", "Julián Álvarez", "Emiliano Martínez",
    "Rodrigo De Paul", "Enzo Fernández", "Alexis Mac Allister", "Carlos Tévez", "Sergio Agüero",
    "Javier Mascherano", "Juan Román Riquelme", "Pablo Aimar", "Hernán Crespo", "Gabriel Batistuta",
    "Javier Zanetti", "Esteban Cambiasso", "Walter Samuel", "Juan Sebastián Verón", "Rivaldo",
    "Kaká", "Roberto Carlos", "Cafu", "Dani Alves", "Marcelo", "Thiago Silva", "Casemiro",
    "Vinícius Jr.", "Rodrygo", "Richarlison", "Gabriel Jesus", "Romário", "Adriano", "Bebeto",
    "Sócrates", "Garrincha", "Franz Beckenbauer", "Gerd Müller", "Miroslav Klose", "Thomas Müller",
    "Philipp Lahm", "Bastian Schweinsteiger", "Mesut Özil", "Marco Reus", "Mats Hummels",
    "Joshua Kimmich", "Jamal Musiala", "Arjen Robben", "Franck Ribéry", "Robin van Persie",
    "Wesley Sneijder", "Clarence Seedorf", "Ruud Gullit", "Marco van Basten", "Johan Cruyff",
    "Dennis Bergkamp", "Patrick Vieira", "Thierry Henry", "Eric Cantona", "Wayne Rooney",
    "David Beckham", "Steven Gerrard", "Frank Lampard", "John Terry", "Rio Ferdinand",
    "Ashley Cole", "Ryan Giggs", "Paul Scholes", "Didier Drogba", "Samuel Eto'o", "Yaya Touré",
    "George Weah", "Riyad Mahrez", "Achraf Hakimi", "Victor Osimhen", "Khvicha Kvaratskhelia",
    "Luis Figo", "Deco", "Pepe", "Bruno Fernandes", "Bernardo Silva", "Rúben Dias", "João Félix",
    "Ricardo Quaresma", "Radamel Falcao", "James Rodríguez", "Juan Cuadrado", "Yerry Mina",
    "David Villa", "Fernando Torres", "Cesc Fàbregas", "David Silva", "Santi Cazorla",
    "Carles Puyol", "Sergio Busquets", "Zlatan Ibrahimović", "Andrea Pirlo", "Alessandro Del Piero",
    "Francesco Totti", "Fabio Cannavaro", "Paolo Maldini", "Leonardo Bonucci", "Giorgio Chiellini",
    "Daniele De Rossi", "Mario Balotelli", "Hakim Ziyech", "Yassine Bounou", "Sofyan Amrabat",
    "Michael Essien", "Pierre-Emerick Aubameyang", "Jay-Jay Okocha", "Nwankwo Kanu", "Thomas Partey",
    "Park Ji-sung", "Keisuke Honda", "Shinji Kagawa", "Takefusa Kubo", "Mehdi Taremi",
    "Tim Cahill", "Carlos Valderrama", "René Higuita", "Claudio Bravo", "Arturo Vidal",
    "Alexis Sánchez", "José Luis Chilavert", "Roque Santa Cruz", "Paolo Guerrero", "Jefferson Farfán",
    "Luis Díaz", "Moisés Caicedo", "Pervis Estupiñán", "Enner Valencia", "Antonio Valencia",
    "Diego Godín", "Diego Forlán", "Federico Valverde", "Darwin Núñez", "Marc-André ter Stegen",
    "Jan Oblak", "Alisson Becker", "Ederson", "Keylor Navas", "Hugo Sánchez", "Jorge Campos",
    "Rafael Márquez", "Javier Hernández"
]

# Eliminar duplicados manteniendo el orden
jugadores_unicos = list(dict.fromkeys(jugadores))
datos_juego = []

headers = {'User-Agent': 'FutbolGamesApp/1.0 (contacto@tuapp.com)'}

print("Obteniendo URLs oficiales de Wikipedia...")
for jugador in jugadores_unicos:
    # Consultar API Rest de Wikipedia
    url_api = f"https://es.wikipedia.org/api/rest_v1/page/summary/{jugador.replace(' ', '_')}"
    try:
        res = requests.get(url_api, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            # Preferir la imagen original sobre el thumbnail recortado
            img_url = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img_url:
                datos_juego.append({
                    "nombre": jugador,
                    "imagen_url": img_url
                })
    except Exception as e:
        print(f"Error cargando {jugador}: {e}")

# Estructura final para tu data.json
json_final = {"jugador_borroso": datos_juego}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(json_final, f, ensure_ascii=False, indent=2)

print(f"¡Éxito! Se guardaron {len(datos_juego)} jugadores válidos en data.json")