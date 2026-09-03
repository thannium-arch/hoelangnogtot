// Dit script laadt centraal de Google AdSense code in voor de hele website.
// Zodra je bent goedgekeurd, vervang je de 'ca-pub-XXXXXXXXXXXXXXXX' door jouw eigen publisher ID.

(function() {
    // Voorkom dubbele scripts als het bestand per ongeluk twee keer wordt geladen
    if (document.getElementById('google-adsense-script')) return;

    const adScript = document.createElement('script');
    adScript.id = 'google-adsense-script';
    adScript.async = true;
    
    // VERVANG DEZE LINK STRAKS DOOR JOUW UNIEKE ADSENSE LINK
    adScript.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX";
    adScript.crossOrigin = "anonymous";
    
    // Voeg het script toe aan de head van de pagina
    document.head.appendChild(adScript);
})();
