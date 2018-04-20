var pressed = false;
$(document).keydown(function (e) {
    document.write(e.which);
    if (e.which == 87) {
        up();
        pressed = true;
    }
    if (e.which == 82) {
        up();
        pressed = true;
    }

    if (e.which == 83) {
        down();
        pressed = true;
    }
    if (e.which == 65) {
        left();
        pressed = true;
    }
    if (e.which == 68) {
        right();
        pressed = true;
    }
    if (e.which == 76) {
        calibrate();
    }
});

$(document).keyup(function (e) {
    //document.write(e.which);
    if (pressed == true) {

        if (e.which == 87) {
            stop();
        }
        if (e.which == 83) {
            stop();
        }
        if (e.which == 65) {
            stop();
        }
        if (e.which == 68) {
            stop();
        }
    }
});

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function moveBar(w) {
    var bar = document.getElementById('distanceBar');
    bar.style = "width : " + w + "%";
    bar.textContent = w + " cm"
}

function calibrate() {
    document.getElementById('calibrate_text').innerHTML = "Start calibration";
    readData();
}

function readData() {
    $.getJSON("scan",
    function (data) {
        chart.series[0].setData(data);
    });
}

function up() {
    $.getJSON('/up', {
        prolang: $('input[name="prolang"]').val(),
    }, function (data) {
    });
}

function down() {
    $.getJSON('/down', {
        prolang: $('input[name="prolang"]').val(),
    }, function (data) {
        //chart.series[1].setData([{'x': x, 'y': y,'z': 30}]);
        //moveBar(data);

    });
}

function stop() {
    $.getJSON('/stop', {
        prolang: $('input[name="prolang"]').val(),
    }, function (data) {
        $.each(data, function (key, val) {
            if (key == 'y') {
                y = val;
                
            }
            else if (key == "x") {
                x = val;
                
            } 
            else if(key == "distance"){
                moveBar(val);
            }
            else if(key == "angle"){
                document.getElementById('angle').innerHTML = "Angle: " + angle + " degrees";
            }
        });
        //x = x + distance * Math.cos(angle);
        //y = y + distance * Math.sin(angle);
        document.getElementById('data').innerHTML = "X: " + x +"Y:"+y;
        document.getElementById('distance').innerHTML = "Distance: " + y + "cm";
        
        chart.series[1].setData([{ 'x': x, 'y': y, 'z': 30 }]);

    });
}

function right() {
    $.getJSON('/right', {
        prolang: $('input[name="prolang"]').val(),
    }, function (data) {
        //moveBar(data);
    });

}

function left() {
    $.getJSON('/left', {
        prolang: $('input[name="prolang"]').val(),
    }, function (data) {
        //moveBar(data);
    });
}

function music() {
    $.getJSON('/music', {
        prolang: $('input[name="prolang"]').val(),
    }, function (data) {

    });
}

function getPos(e) {
    //x=e.clientX;
    //y=e.clientY;
    //cursor="Your Mouse Position Is : " + x + " and " + y ;
    //document.getElementById("Y").innerHTML=cursor
    e = chart.pointer.normalize(e);
    $("#X").text(e.chartX - chart.plotLeft);
    $("#Y").text(600 - (e.chartY - chart.plotTop));
}
