




$('.modal').modal();

$('#tech').click(function () {
	$('#tech').prop('checked') ? $('#tech-c').fadeIn() : $('#tech-c').fadeOut();

});

$('#oper').click(function () {
	$('#oper').prop('checked') ? $('#oper-c').fadeIn() : $('#oper-c').fadeOut();
});

$('#sps').click(function () {
	$('#sps').prop('checked') ? $('#sps-c').fadeIn() : $('#sps-c').fadeOut();
});

$('#send').click(function () {
	var selectedFile = document.getElementById('input').files[0];
	if (selectedFile.name.includes(".csv")) {
		Papa.parse(selectedFile, {
			download: true,
			complete: function (results) {
				console.log(results);
				res = results;
				genCharts();
			}
		});
	} else {
		alert("Sorry! Only csv files allowed!")
	}

});
