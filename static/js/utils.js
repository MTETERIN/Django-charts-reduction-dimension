var chartColors = [
	'rgba(255, 99, 132, 0.5)',
	'rgba(255, 159, 64, 0.5)',
	'rgba(255, 205, 86, 0.5)',
	'rgba(75, 192, 192, 0.5)',
	'rgba(54, 162, 235, 0.5)',
	'rgba(153, 102, 255, 0.5)',
	'rgba(201, 203, 207, 0.5)'
];

function randomColor() {
		return chartColors[Math.floor(Math.random()*6)];
	};



var parameters = {};
parameters['50']="Power consumption on the meter №1 (Energieverbr._Auftr._Zaehler1)";
parameters['51']="Power consumption on the meter №2 (Energieverbr._Auftr._Zaehler2)";
parameters['102']="Melt pressure in extruder B (ExtB_Ist_Massedruck)";
parameters['138']="Melt pressure in extruder С (ExtC_Ist_Massedruck)";
parameters['145']="Melt temperature of extruder C (ExtC_IST_Temp_Massetemperatur_vor_Sieb)";
parameters['151']="Melt temperature of zone №4 of extruder C (ExtC_IST_Temp_Zone4)";
parameters['170']="Weight of the composition (IST_Gewicht_Komp3)";
parameters['203']="Preliminary property (Vorabzug_Zugist)";

function getparamNameMultiValues(paramName){
	var sURL = window.document.URL.toString();
	var value =[];
	if (sURL.indexOf("?") > 0){
		var arrParams = sURL.split("?");
		var arrURLParams = arrParams[1].split("&");
		for (var i = 0; i<arrURLParams.length; i++){
			var sParam =  arrURLParams[i].split("=");
			console.log(sParam);
			if(sParam){
				if(sParam[0] == paramName){
					if(sParam.length>0){
						value.push(sParam[1].trim());
					}
				}
			}
		}
	}
	return value.toString();
}
