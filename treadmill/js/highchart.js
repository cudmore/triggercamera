var mychart = function(p) {
    var chart;
    chart = new Highcharts.Chart({
        chart: {
            renderTo: 'chart', 
            defaultSeriesType: 'line',
            events: {
                load: function() {
                    // Each time you receive a value from the socket, I put it on the graph
                    socket.on('temperatureUpdate', function (msg) {
                        json = $.parseJSON(msg)
                        var series = chart.series[0];
                        var xFloat = parseFloat(json.x);
                        var yFloat = parseFloat(json.y);
                        series.addPoint([xFloat, yFloat]);
                        
                        var series2 = chart.series[1];
                        series2.addPoint([xFloat, yFloat*2]);

                        var series3 = chart.series[2];
                        series3.addPoint([xFloat, yFloat*4]);
                    });
                }
            }
        },
        rangeSelector: {
            selected : 100
        },
        title: {
            text: 'CPU Temperature Raspberry Pi'
        },
        xAxis: {
            minPadding: 0.2,
            maxPadding: 0.2,
            type: 'datetime',
            //tickPixelInterval: 150,
            //maxZoom: 20 * 1000
        },
        yAxis: {
            minPadding: 0.2,
            maxPadding: 0.2,
            title: {
                text: 'Temperature ºC',
                margin: 80
            }
        },
        series: [{
            name: 'Temperature',
            data: []
        },
        {
            name: 'Temperature2',
            data2: []
        },
        {
            name: 'Temperature3',
            data3: []
        }
        ]
    });
}