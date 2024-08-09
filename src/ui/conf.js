// const BASEURL = process.env.VUE_APP_BASE_URL || '/api';
const BASEURL = "/api";

const settings = {
  token: "",
  headers: new Headers({
    Accept: "application/json",
  }),
  csrf: () => {
    return document.getElementById("csrf-token").value;
  },
  baseURL: BASEURL,
  attribution:
    "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
  baseLayer:
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
};

export default settings;
