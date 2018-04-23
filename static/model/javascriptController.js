function newFunction() {
    {
        "plugins";
        ["jsdom-quokka-plugin"];
    }
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

async function reset() {
    obj = [];
    $.getJSON('/reset_pos', {
        prolang: $('input[name="prolang"]').val(),
    }, function (data) {

    });
}

function machine_learning() {
    obj = [];
    $.getJSON('/machine_learning', {
        prolang: $('input[name="prolang"]').val(),
    }, function (data) {

    });

}
$(document).keydown(async function (e) {
    //document.write(e.which);
    if (e.which == 87) {
        up();
        pressed = true;
        console.log("UP been pressed");
    }

    if (e.which == 82) {
        await reset();
        pressed = true;
    }

    if (e.which == 83) {
        await down();
        pressed = true;
    }
    if (e.which == 65) {
        await left();
        pressed = true;
    }
    if (e.which == 68) {
        await right();
        pressed = true;
    }

    if (e.which == 76) {
        if (pressed == false) {
            await calibrate();
            pressed = true;
        }
    }
});

$(document).keyup(async function (e) {
    //document.write(e.which);
    if (pressed == true) {

        if (e.which == 87) {
            await stop();
            console.log("UP been released");
            pressed = false;
        }
        if (e.which == 83) {
            await stop();
            pressed = false;
        }
        if (e.which == 65) {
            await stop();
            pressed = false;
        }
        if (e.which == 68) {
            await stop();
            pressed = false;
        }
        if (e.which == 76) {
            pressed = false;
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

async function calibrate() {
    document.getElementById('calibrate_text').innerHTML = "Start calibration";
    await readData();
}

async function readData() {
    $.getJSON("/scan",
        function (data) {
            chart.series[0].setData(data);
            document.getElementById('calibrate_text').innerHTML = "Finished calibration";
        });
}

function up() {
    $.getJSON('/up',
    function (data) {
    });
    
}

function down() {
    $.getJSON('/down'
    , function (data) {
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
            else if (key == "distance") {
                moveBar(val);
            }
            else if (key == "angle") {
                document.getElementById('angle').innerHTML = "Angle: " + val + " degrees";
            }
            else if (key == 'obj') {
                obj.push(val);
                console.log(obj);
                chart.series[0].setData(obj);
            }
        });
        //x = x + distance * Math.cos(angle);
        //y = y + distance * Math.sin(angle);
        document.getElementById('data').innerHTML = "X: " + x + "Y:" + y;
        document.getElementById('distance').innerHTML = "Distance: " + y + "cm";

        chart.series[1].setData([{ 'x': x, 'y': y, 'z': 30 }]);

    });
}
