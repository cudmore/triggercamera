           var server_json = '';
           //var trialIsRunning = 0;
           
            var namespace = ''; // change to an empty string to use the global namespace

            // the socket.io documentation recommends sending an explicit package upon connection
            // this is specially important when using the global namespace
            console.log('index.html is creating socket');
            var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
		
            // event handler for new connections
            socket.on('connect', function() {
                socket.emit('my event', {data: 'I\'m connected!'});
            });

			//$('#chart').hide() //chart is initially hidden
			
			$('#hideshowchart').click(function(event) {        
				 jQuery('#chart').toggle('show');
			});
			
			$('#hideshowserverstate').click(function(event) {        
				 jQuery('#serverstate').toggle('show');
			});
			$('#serverstate').hide() //chart is initially hidden
			
			$('#hideshowtrialplotdiv').click(function(event) {        
				 jQuery('#trialPlotDivID').toggle('show');
			});

            socket.on('serverUpdate', function(msg) {
                //console.log('received serverUpdate');
                	json = $.parseJSON(msg);
                	server_json = json;
                	$('#serverDateTimeID').empty().append(json.currentdate + " " + json.currenttime);
                	
                	$('#savePathID').empty().append('Save path: ' + json.savepath);
                	$('#currentAnimalID').empty().append('Animal ID: ' + json.animalID);
                	                	
                	$('#currentTrialFileID').empty().append('File: ' + json.fileName);

                	$('#currentTrialNumberID').empty().append('Trial : ' + json.trialNumber);
                	
                	numEpochStr = parseInt(json.numEpoch) - 1
                	$('#currentEpochNumberID').empty().append('Epoch : ' + json.epochNumber + '/' + numEpochStr);
                	$('#currentDurID').empty().append('Duration (ms): ' + json.trialDur);
                	$('#currentUseMotorID').empty().append('Use Motor: ' + json.useMotor);
                	$('#currentMotorDelID').empty().append('Motor Delay (ms): ' + json.motorDel);
                	$('#currentMotorDurID').empty().append('Motor Duration (ms): ' + json.motorDur);
                	
                	//$('#currentDurID').empty().append('Duration (ms): ' + json.dur);
                	
                	if (json.trialRunning=='1') {
                		trialspinner(1)
                	} else {
                		trialspinner(0)
                	}
            });
			
            socket.on('serialdata', function(msg) {
                //console.log('index.html received serialdata:' + msg.data);
                $('#serialDataID').append(msg.data + "<br>");
                $('#newDataID').empty().append(msg.data);
                
                if (msg.data == '=== Trial Form Done ===') {
					arduinoUploadSpinner(0)
               	}
                if (msg.data.search('=== Start Trial')==0) {
					trialspinner(1)
               	}
                if (msg.data.search('=== Stop Trial')==0) {
					trialspinner(0)
               	}
            });

            //socket.on('newdata', function(msg) {
            //    console.log("newdata:" + msg.data);
            //    $('#newDataID').empty().append("newdata: '" + msg.data + "'");
            //});

            // event handler for server sent data
            // the data is displayed in the "Received" section of the page
            socket.on('my response', function(msg) {
                $('#log').empty().append("my response: '" + msg.data + "'");
            });

            
            //when user 'upload trial', we get back a plotly plot div of what the stim look like
            socket.on('trialPlotDiv', function(msg) {
                $('#trialPlotDivID').empty().append(msg.data);
            });

            $('form#animalform').submit(function(event) {
                animalformDict = {animalID: $('#animalID').val()};
                socket.emit('animalform', animalformDict);
                return false;
            });

			$("ardinput").attr({
				"min" : 0          // values (or variables) here
			});

			$('form#trialform').submit(function(event) {
				trialFormDict = {
					numEpoch: $('#numEpochID').val(),
					epochDur: $('#epochDurID').val(),

					preDur: $('#preDurID').val(),
					postDur: $('#postDurID').val(),
					numPulse: $('#numPulseID').val(),
					pulseDur: $('#pulseDurID').val(),
					//useMotor = {motorOn, motorLocked, motorFree}
					useMotor: $('input[name=motorRadio]:checked').val(),
					motorDel: $('#motorDelID').val(),
					motorDur: $('#motorDurID').val(),
					motorSpeed: $('#motorSpeedID').val()
				};
				//console.log("(2) trialFormDict.useMotor:" + trialFormDict.useMotor);
				console.log('index.html is sending trialform:' + trialFormDict);
				
				//turn on spinner
				arduinoUploadSpinner(1)
				
				//upload
				socket.emit('trialform', trialFormDict);
				
				return false;
			});

			$("#startarduinoButtonID").click(function() {
				trialspinner(1);
				socket.emit('startarduinoButtonID', {data: ''});
				//$("#ex1").slider("enable");
                return false;
			});

			$("#stoparduinoButtonID").click(function() {
				socket.emit('stoparduinoButtonID', {data: ''});
				//$("#ex1").slider("enable");
				trialspinner(0);
                return false;
			});

			function trialspinner(start) {
				//if (trialIsRunning == 0) {
				if (start) {
					//console.log("startspinnerID")
					$("body").css("cursor", "progress");
					$('#faSpinnerID').removeClass()
					$('#faSpinnerID').addClass('greencolor fa fa-circle-o-notch  fa-2x fa-spin')
					//setTimeout(function() { $('.fa').removeClass().addClass('fa fa-minus-circle') }, 1000);
				} else {
					//console.log("stopspinnerID")
					$("body").css("cursor", "default");
					$('#faSpinnerID').removeClass()
					$('#faSpinnerID').addClass('blackcolor fa fa-circle-o-notch  fa-2x')
					//setTimeout(function() { $('.fa').removeClass().addClass('fa fa-minus-circle') }, 1000);
				}
			}

			function arduinoUploadSpinner(start) {
				if (start) {
					console.log("startspinnerID")
					$("body").css("cursor", "progress");
					$('#faSpinnerArduinoID').removeClass()
					$('#faSpinnerArduinoID').addClass('redcolor fa fa-circle-o-notch  fa-1x fa-spin')
				} else {
					console.log("stopspinnerID")
					$("body").css("cursor", "default");
					$('#faSpinnerArduinoID').removeClass()
					$('#faSpinnerArduinoID').addClass('blackcolor fa fa-circle-o-notch  fa-1x')
				}
			}
			
			//$('#serialDataID').hide() //serialDataID is initially hidden
			//$('#utilityID').hide() //serialDataID is initially hidden

			//one callback for lots of buttons, each button needs class="xxx" and a unique id=""
			$(".buttonCallback").click(function() {
			  //alert(this.id);
			  if (this.id == "checkserialportID") {
			  	socket.emit('checkserialportID', {data: ''});
			  } else if (this.id == "arduinoVersionID") {
			  	socket.emit('arduinoVersionID', {data: ''});
			  } else if (this.id == "printArduinoStateID") {
			  	socket.emit('printArduinoStateID', {data: ''});
			  } else if (this.id == "emptySerialID") {
			  	socket.emit('emptySerialID', {data: ''});
			  } else if (this.id == "hideshowseriallog") {
			  	$('#serialDataID').toggle('show');
			  } else if (this.id == "hideshowutility") {
			  	$('#utilityID').toggle('show');
			  } else if (this.id == "clearSerialLogID") {
			  	$("#serialDataID").empty();
			  } else if (this.id == "serialPortButtonID") {
			  	var serialPortText = $('#serialPortTextID').val();
			  	//console.log(serialPortText);
			  	socket.emit('setSerialPortID', {data: serialPortText});
			  }
			  return false;
			});

//<!-- -->
    var trialStartMillis;
    var motorStartMillis;
    var motorStopMillis;
    var chart;
    chart = new Highcharts.Chart({
        chart: {
            renderTo: 'chart', 
            defaultSeriesType: 'line',
            events: {
                load: function() {
                    // Each time you receive a value from the socket, I put it on the graph
                    socket.on('serialdata', function (msg) {
						//serialdata is of form {millis, event, val}
						//console.log("chart received serialdata:" + msg.data)
						res = msg.data.trim().split(",");
						var millis = parseFloat(res[0]) / 1000;
						var event = res[1];
						var val = res[2];
						//on 'new trial' reset x-axis
						//var xMin = lastTrialStartMillis;
						//var xMax = lastTrialStartMillis + 10000;
						//1
						if (event == "startTrial") {
                        	trialStartMillis = millis;
                        	millis = millis - trialStartMillis;
                        	
                        	//clear chart
                        	chart.series[0].setData([]);
                        	chart.series[1].setData([]);
                        	chart.series[2].setData([]);
                        	//chart.series[3].setData([]); //motor dots
							chart.xAxis[0].removePlotLine('startTrial');
							chart.xAxis[0].removePlotLine('stopTrial');
							chart.xAxis[0].removePlotBand('motorBand');
							chart.xAxis[0].removePlotBand('scanImageBand');
							
							//set min/max of x-axis
							//console.log("treadmill.trial['dur']=" + {{treadmill.trial['dur']}});
							//var trialSeconds = {{ treadmill.trial['dur'] }} / 1000;
							
							var trialSeconds = server_json.trialDur / 1000;
							
							chart.xAxis[0].setExtremes(-0.5, trialSeconds+0.5);
							
                        	var series = chart.series[0];
                        	series.addPoint([millis, 1], false);

							chart.xAxis[0].addPlotLine({
								value: millis,
								color: 'green',
								width: 2,
								id: 'startTrial'
							});

						} else if (event == "stopTrial") {
                         	millis = millis - trialStartMillis;
	                       	var series = chart.series[0];
                        	series.addPoint([millis, 1], false);

							chart.xAxis[0].addPlotLine({
								value: millis,
								color: 'red',
								width: 2,
								id: 'stopTrial'
							});
						//3
						} else if (event == "motorstart") {
                          	millis = millis - trialStartMillis;
	                       	motorStartMillis = millis;
	                       	//var series3 = chart.series[2];
                        	//series3.addPoint([millis, 3]);
						} else if (event == "motorstop") {
                         	millis = millis - trialStartMillis;
	                       	motorStopMillis = millis;
                        	//var series3 = chart.series[2];
                        	//series3.addPoint([millis, 3], false);
					
							if (1) {
								chart.xAxis[0].addPlotBand({
									from: motorStartMillis,
									to: motorStopMillis,
									color: '#EEBBBB',
									id: 'motorBand'
								});
							}
						//2
						} else if (event == "scanimagestart") {
                         	millis = millis - trialStartMillis;
                        	var series2 = chart.series[1];
                        	series2.addPoint([millis, 2], false);
						} else if (event == "scanimageframe") {
                         	millis = millis - trialStartMillis;
                        	//var series2 = chart.series[1];
                        	//series2.addPoint([millis, 2], false);
								chart.xAxis[0].addPlotBand({
									from: millis,
									to: millis+0.01,
									color: '#BBEEBB',
									id: 'scanImageBand'
								});
						} else if (event == "rotary") {
                          	millis = millis - trialStartMillis;
                          	//console.log(millis);
	                       	var series4 = chart.series[3];
                        	series4.addPoint([millis, 3.5], false);
						}						
						//redraw once
						chart.redraw()
                    });
                }
            }
        },
        rangeSelector: {
            selected : 100
        },
        title: {
            //text: 'Treadmill Trial'
            text: ''
        },
		credits: {
			  enabled: false
		  },
        xAxis: {
            minPadding: 0.1,
            maxPadding: 0.1,
            type: 'linear', //type: 'datetime',
            //tickPixelInterval: 150,
            //maxZoom: 20 * 1000
            title: {
                text: 'Seconds',
                //margin: 80
            }
        },
        yAxis: {
            minPadding: 0.1,
            maxPadding: 0.1,
            labels: { enabled: false },
            title: {
                text: 'Events',
                //margin: 80
            }
        },
        series: [{
            name: 'Trial',
            color: 'black',
            lineWidth: 0,
            data: []
        },
        {
            name: 'ScanImage',
            color: 'green',
            lineWidth: 0,
            data2: []
        },
        {
            name: 'Motor',
            color: 'red',
            lineWidth: 0,
            data3: []
        },
        {
            name: 'Rotary',
            color: 'black',
            lineWidth: 0,
            data4: []
        }
        ]
    });


		//
		// led1 and led2
		var RGBChange = function() {
			//$('#RGB').css('background', 'rgb('+r.getValue()+','+g.getValue()+','+b.getValue()+')')
		};

		var led1 = $('#led1ID').slider()
				.on('slide', RGBChange)
				.data('slider');
		var led2 = $('#led2ID').slider()
				.on('slide', RGBChange)
				.data('slider');

		//$("#R").slider("disable");
		$('#led1On').click(function(event) {        
			 jQuery('#led1ID').slider('enable');
		});
		$('#led1Off').click(function(event) {        
			 jQuery('#led1ID').slider('disable');
		});
		$('#led2On').click(function(event) {        
			 jQuery('#led2ID').slider('enable');
		});
		$('#led2Off').click(function(event) {        
			 jQuery('#led2ID').slider('disable');
		});

