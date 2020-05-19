import bs4 as bs
import requests
import sqlite3
import sys

class Match:
    def __init__(self,  link):
        page = requests.get("https://www.hltv.org" + link)
        soup = bs.BeautifulSoup(page.content, "html.parser")
        self.teams = []
        self.results = []
        self.maps = []
        self.link = link

        try:
            self.unix = (str(soup.find('div', class_='date')))
            self.unix = self.unix.split("=")
            self.unix = self.unix[3].split('"')
            self.unix = int(self.unix[1])

            for team in soup.find_all('div', class_='teamName'):
                self.teams.append(team.text)

            for result in soup.find_all('div', class_='results'):
                result = result.text.split(':')
                self.results.append(result[0])
                result = result[1].split()
                self.results.append(result[0])

            for map_name in soup.find_all('div', class_='mapname'):
                self.maps.append(map_name.text)

        except requests.exceptions.RequestException:
            pass

    def show(self):
        print(self.teams)
        print(self.results)
        print(self.maps)
        print(self.link)
        print(self.unix)

    def add_to_db(self, conn, c):
        for n in range(int(len(self.results) / 2)):
            c.execute("INSERT INTO Matches (team1, team2, result1, result2, map, unix, link)"
                      "VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (self.teams[0], self.teams[1], self.results[n*2], self.results[n*2+1],
                       self.maps[n], self.unix, self.link))

    def check_for_duplicate(self, c):
        for n in range(int(len(self.results) / 2)):
            c.execute("SELECT * FROM Matches WHERE (link = ? AND map = ?)", (self.link, self.maps[n]))
            duplicate = c.fetchall()
            return not duplicate


def get_links(offset):
    links = []
    try:
        page = requests.get("https://www.hltv.org/results?offset=" + str(offset))
        soup = bs.BeautifulSoup(page.content, "html.parser")

        match_links = soup.find_all('div', class_='result-con')

        for match_link in match_links:
            match_link = match_link.a.get('href')
            links.append(match_link)

        return links

    except requests.exceptions.RequestException:
        pass


def create_table():
    conn = sqlite3.connect('games.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS Matches(team1 TEXT, team2 TEXT, result1 INTEGER, result2 INTEGER,'
              'map TEXT, unix INTEGER, link TEXT)')
    c.close()
    conn.close()


def scrape(nPages: int):
    conn = sqlite3.connect('games.db')
    c = conn.cursor()


    for x in range(nPages):
        x *= 100
        for link in get_links(x):
            link = Match(link)
            if link.check_for_duplicate(c):
                link.show()
                link.add_to_db(conn, c)

    c.execute("SELECT * FROM Matches ORDER BY unix DESC")
    conn.commit()
    c.close()
    conn.close()


if __name__ == '__main__':
    nPages = int(sys.argv[1])
    scrape(nPages)




