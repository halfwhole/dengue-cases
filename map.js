const MAX_OPACITY_NUM = 100;
const MAX_OPACITY = 0.8;

const map = L.map('map').setView([1.35, 103.82], 12);
let jsons;
let geoJsonLayer;

L.tileLayer('http://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
    attribution: '',
    minZoom: 11,
    maxZoom: 18
}).addTo(map);

// Populates the 'jsons' variable
async function populateJsons(filename) {
    function getFilenames() {
        return new Promise((res, rej) => {
            jQuery.ajax({
                type: 'POST',
                url: 'dir.php',
                dataType: 'json',
                success: (data) => res(data)
            });
        });
    }

    function getJson(filename) {
        return new Promise((res, rej) => {
            fetch(`data/${filename}.json`).then(res => res.json()).then(data => res(data));
        });
    }

    const filenames = await getFilenames();
    const jsonsPromises = filenames
          .filter(filename => filename != 'data-latest')
          .map(filename => getJson(filename));
    jsons = await Promise.all(jsonsPromises);
}


// Displays the GeoJSON for the specified index in 'jsons'
function displayGeoJson(index) {
    function style(feature) {
        const min = (a, b) => a < b ? a : b;
        const case_size = feature.properties.case_size;
        if (case_size >= 10) {
            return {color: 'red', weight: 2, fillOpacity: min(case_size / MAX_OPACITY_NUM * MAX_OPACITY, MAX_OPACITY)};
        } else {
            return {color: 'orange', weight: 2};
        }
    }

    function onEachFeature(feature, layer) {
        const description = feature.properties.description;
        const case_size = feature.properties.case_size;
        const homes = feature.properties.homes;
        const public_places = feature.properties.public_places;
        const construction_sites = feature.properties.construction_sites;

        let popupContent = `<b>Cluster: </b>${description}<br/><b>Case Size: </b>${case_size}`
        if (homes) popupContent += `<br/><b>Homes: </b>${homes}`
        if (public_places) popupContent += `<br/><b>Public Places: </b>${public_places}`
        if (construction_sites) popupContent += `<br/><b>Construction Sites: </b>${construction_sites}`

        layer.bindPopup(popupContent);
    }

    if (geoJsonLayer) geoJsonLayer.clearLayers();
    const data = jsons.slice(index)[0];
    geoJsonLayer = L.geoJSON(data, {
        onEachFeature: onEachFeature,
        style: style
    });
    geoJsonLayer.addTo(map);
}


// Event handler for HTML slider update
function sliderUpdate(value) {
    displayGeoJson(value - 1);
}


// Enables the slider and makes it visible
function enableSlider() {
    slider = document.getElementById('slider');
    slider.style.visibility = 'visible';
    slider.min = 1;
    slider.max = jsons.length;
    slider.value = jsons.length;
}


async function main() {
    await populateJsons();
    enableSlider();
    displayGeoJson(-1);
}

main();
