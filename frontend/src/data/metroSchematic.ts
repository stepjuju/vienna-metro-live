
/**
 * Diagram coordinates in the January 2026 Vienna SVG (1122.5 × 793.7).
 * These are schematic station positions, NOT longitude/latitude.
 * Each list follows the direction of the matching SVG path in metroPaths.json.
 * Retain the original SVG's CC BY-SA 4.0 attribution in the repository.
 */

export const LINES = ['U1', 'U2', 'U3', 'U4', 'U6'] as const

export type LineId = (typeof LINES)[number]

export type Anchor = {
  stationId: string
  name: string
  x: number
  y: number
  interchange?: boolean
}

const s = (
  stationId: string,
  name: string,
  x: number,
  y: number
): Anchor => ({ stationId, name, x, y })

export const LINE_STATIONS: Record<LineId, readonly Anchor[]> = {
  // U1 path: Oberlaa → Leopoldau (interchange coordinates calibrated from SVG)
  U1: [
  { stationId: 'vie-oberlaa', name: 'Oberlaa', x: 698.82, y: 771.94 },
  { stationId: 'vie-neulaa', name: 'Neulaa', x: 668.4, y: 741.8 },
  { stationId: 'vie-alaudagasse', name: 'Alaudagasse', x: 637.1, y: 710.9 },
  { stationId: 'vie-altes-landgut', name: 'Altes Landgut', x: 605.9, y: 680.1 },
  { stationId: 'vie-troststrasse', name: 'Troststraße', x: 574.6, y: 649.2 },
  { stationId: 'vie-reumannplatz', name: 'Reumannplatz', x: 543.3, y: 618.3 },
  { stationId: 'vie-keplerplatz', name: 'Keplerplatz', x: 512.1, y: 587.5 },
  { stationId: 'vie-suedtiroler-pl-hbf', name: 'Südtiroler Pl. - Hbf.', x: 491.3, y: 546.1 },
  { stationId: 'vie-taubstummengasse', name: 'Taubstummengasse', x: 491.3, y: 500.1 },
  { stationId: 'vie-karlsplatz', name: 'Karlsplatz', x: 491.33, y: 453.5, interchange: true },
  { stationId: 'vie-stephansplatz', name: 'Stephansplatz', x: 529.2, y: 359.0, interchange: true },
  { stationId: 'vie-schwedenplatz', name: 'Schwedenplatz', x: 638.0, y: 302.38, interchange: true },
  { stationId: 'vie-nestroyplatz', name: 'Nestroyplatz', x: 688.9, y: 302.4 },
  { stationId: 'vie-praterstern', name: 'Praterstern', x: 738.0, y: 302.42, interchange: true },
  { stationId: 'vie-vorgartenstrasse', name: 'Vorgartenstraße', x: 794.5, y: 281.2 },
  { stationId: 'vie-donauinsel', name: 'Donauinsel', x: 821.2, y: 254.7 },
  { stationId: 'vie-kaisermuehlen-vic', name: 'Kaisermühlen-VIC', x: 848.0, y: 228.2 },
  { stationId: 'vie-alte-donau', name: 'Alte Donau', x: 874.7, y: 201.7 },
  { stationId: 'vie-kagran', name: 'Kagran', x: 901.5, y: 175.1 },
  { stationId: 'vie-kagraner-platz', name: 'Kagraner Platz', x: 928.3, y: 148.6 },
  { stationId: 'vie-rennbahnweg', name: 'Rennbahnweg', x: 955.0, y: 122.1 },
  { stationId: 'vie-aderklaaer-strasse', name: 'Aderklaaer Straße', x: 981.8, y: 95.5 },
  { stationId: 'vie-grossfeldsiedlung', name: 'Großfeldsiedlung', x: 1008.5, y: 69.0 },
  { stationId: 'vie-leopoldau', name: 'Leopoldau', x: 1039.11, y: 38.76 },
  ],

  // U2 path: Karlsplatz → Seestadt
  U2: [
    s('vie-karlsplatz', 'Karlsplatz', 491.34, 454.42),
    s('vie-museumsquartier', 'Museumsquartier', 450.2, 412.4),
    s('vie-volkstheater', 'Volkstheater', 434.65, 359.06),
    s('vie-rathaus', 'Rathaus', 434.65, 322.06),
    s('vie-schottentor', 'Schottentor', 477.41, 259.60),
    s('vie-schottenring', 'Schottenring', 585.83, 245.67),
    s('vie-taborstrasse', 'Taborstraße', 660.4, 245.67),
    s('vie-praterstern', 'Praterstern', 737.68, 302.42),
    s('vie-messe-prater', 'Messe-Prater', 771.4, 335.5),
    s('vie-krieau', 'Krieau', 802.4, 366.5),
    s('vie-stadion', 'Stadion', 833.5, 397.5),
    s('vie-donaumarina', 'Donaumarina', 868.43, 426.47),
    s('vie-donaustadtbruecke', 'Donaustadtbrücke', 908.9, 395.4),
    s('vie-stadlau', 'Stadlau', 932.2, 372.0),
    s('vie-hardeggasse', 'Hardeggasse', 955.5, 348.7),
    s('vie-donauspital', 'Donauspital', 978.8, 325.3),
    s('vie-aspernstrasse', 'Aspernstraße', 1002.1, 302.0),
    s('vie-lina-loos-platz', 'Lina-Loos-Platz', 1025.4, 278.7),
    s('vie-hausfeldstrasse', 'Hausfeldstraße', 1048.7, 255.3),
    s('vie-aspern-nord', 'Aspern Nord', 1072.0, 232.0),
    s('vie-seestadt', 'Seestadt', 1093.66, 209.40),
  ],

  // U3 path: Simmering → Ottakring
  U3: [
    s('vie-simmering', 'Simmering', 880.35, 653.58),
    s('vie-enkplatz', 'Enkplatz', 850.1, 623.3),
    s('vie-zippererstrasse', 'Zippererstraße', 819.0, 592.3),
    s('vie-gasometer', 'Gasometer', 788.0, 561.2),
    s('vie-erdberg', 'Erdberg', 757.0, 530.2),
    s('vie-schlachthausgasse', 'Schlachthausgasse', 725.9, 499.2),
    s('vie-kardinal-nagl-platz', 'Kardinal-Nagl-Platz', 694.9, 468.1),
    s('vie-rochusgasse', 'Rochusgasse', 663.9, 437.1),
    s('vie-landstrasse', 'Landstraße', 632.77, 406.00),
    s('vie-stubentor', 'Stubentor', 566.13, 359.06),
    s('vie-stephansplatz', 'Stephansplatz', 529.13, 359.06),
    s('vie-herrengasse', 'Herrengasse', 481.9, 359.06),
    s('vie-volkstheater', 'Volkstheater', 434.65, 359.06),
    s('vie-neubaugasse', 'Neubaugasse', 395.4, 359.06),
    s('vie-zieglergasse', 'Zieglergasse', 346.2, 359.06),
    s('vie-westbahnhof', 'Westbahnhof', 292.73, 359.06),
    s('vie-schweglerstrasse', 'Schweglerstraße', 247.2, 332.2),
    s('vie-johnstrasse', 'Johnstraße', 216.1, 301.2),
    s('vie-huetteldorfer-strasse', 'Hütteldorfer Straße', 185.1, 270.1),
    s('vie-kendlerstrasse', 'Kendlerstraße', 153.3, 239.4),
    s('vie-ottakring', 'Ottakring', 127.07, 213.10),
  ],

  // U4 path: Hütteldorf → Heiligenstadt
  U4: [
    s('vie-huetteldorf', 'Hütteldorf', 37.795, 302.36),
    s('vie-ober-st-veit', 'Ober St. Veit', 64.6, 329.2),
    s('vie-unter-st-veit', 'Unter St. Veit', 92.2, 356.8),
    s('vie-braunschweiggasse', 'Braunschweiggasse', 119.8, 384.4),
    s('vie-hietzing', 'Hietzing', 147.4, 412.0),
    s('vie-schoenbrunn', 'Schönbrunn', 175.1, 439.6),
    s('vie-meidling-hauptstrasse', 'Meidling Hauptstraße', 230.1, 453.54),
    s('vie-laengenfeldgasse', 'Längenfeldgasse', 302.37, 453.54),
    s('vie-margaretenguertel', 'Margaretengürtel', 346.2, 453.54),
    s('vie-pilgramgasse', 'Pilgramgasse', 395.4, 453.54),
    s('vie-kettenbrueckengasse', 'Kettenbrückengasse', 441.0, 453.54),
    s('vie-karlsplatz', 'Karlsplatz', 491.33, 453.54),
    s('vie-stadtpark', 'Stadtpark', 565.0, 453.54),
    s('vie-landstrasse', 'Landstraße', 632.77, 406.00),
    s('vie-schwedenplatz', 'Schwedenplatz', 638.25, 302.39),
    s('vie-schottenring', 'Schottenring', 585.83, 245.67),
    s('vie-rossauer-laende', 'Roßauer Lände', 545.7, 205.6),
    s('vie-friedensbruecke', 'Friedensbrücke', 509.5, 169.3),
    s('vie-spittelau', 'Spittelau', 491.34, 113.37),
    s('vie-heiligenstadt', 'Heiligenstadt', 491.34, 56.69),
  ],

  // U6 path: Floridsdorf → Siebenhirten
  U6: [
    s('vie-floridsdorf', 'Floridsdorf', 839.82, 48.85),
    s('vie-neue-donau', 'Neue Donau', 804.8, 83.8),
    s('vie-handelskai', 'Handelskai', 735.5, 113.3),
    s('vie-dresdner-strasse', 'Dresdner Straße', 652.4, 113.3),
    s('vie-jaegerstrasse', 'Jägerstraße', 565.9, 113.4),
    s('vie-spittelau', 'Spittelau', 491.34, 113.37),
    s('vie-nussdorfer-strasse', 'Nußdorfer Straße', 418.3, 129.7),
    s('vie-waehringer-strasse-volksoper', 'Währinger Straße-Volksoper', 392.6, 155.4),
    s('vie-michelbeuern-akh', 'Michelbeuern-AKH', 366.9, 181.1),
    s('vie-alser-strasse', 'Alser Straße', 341.2, 206.8),
    s('vie-josefstaedter-strasse', 'Josefstädter Straße', 315.5, 232.5),
    s('vie-thaliastrasse', 'Thaliastraße', 302.1, 279.9),
    s('vie-burggasse-stadthalle', 'Burggasse-Stadthalle', 302.1, 317.2),
    s('vie-westbahnhof', 'Westbahnhof', 302.37, 359.06),
    s('vie-gumpendorfer-strasse', 'Gumpendorfer Straße', 302.5, 403.1),
    s('vie-laengenfeldgasse', 'Längenfeldgasse', 302.37, 453.54),
    s('vie-niederhofstrasse', 'Niederhofstraße', 302.5, 500.8),
    s('vie-bahnhof-meidling', 'Bahnhof Meidling', 302.5, 543.4),
    s('vie-tscherttegasse', 'Tscherttegasse', 302.4, 583.9),
    s('vie-am-schoepfwerk', 'Am Schöpfwerk', 289.4, 618.3),
    s('vie-alterlaa', 'Alterlaa', 258.1, 649.2),
    s('vie-erlaaer-strasse', 'Erlaaer Straße', 226.8, 680.1),
    s('vie-perfektastrasse', 'Perfektastraße', 195.5, 711.0),
    s('vie-siebenhirten', 'Siebenhirten', 165.15, 741.03),
  ],
}

/**
 * Temporary compatibility export.
 * Remove after all remaining consumers migrate to station IDs.
 */
export { stopKey } from '../utils/stopNames'