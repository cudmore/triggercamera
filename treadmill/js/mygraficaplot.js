var mygraficaplot = function(p) {
	//globals
	var plot, plot2;
	//first plot
	var points = [];
	var pointsStart = [];
	var pointsFrame = [];
	var pointsStop = [];
	var pointsMotor = [];
	//seconds plot
	var points2 = [];
	
	var lastTrialStartMillis;
	
	// Initial setup
	p.setup = function() {
		// Create the canvas
		var canvas = p.createCanvas(500, 500);
		p.background(150);

		// Create a new plot and set its position on the screen
		plot = new GPlot(p);
		plot.setPos(25, 25);

		// Set the plot title and the axis labels
		plot.setPoints(points);
		var dataColor = p.color(150,150,150);
		plot.setLineColor(dataColor);
		plot.setPointColor(dataColor);
			plot.addLayer("startTrialLayer", pointsStart);
			plot.getLayer("startTrialLayer").setPointColor(p.color(10, 255, 10));
			plot.addLayer("stopTrialLayer", pointsStop);
			plot.getLayer("stopTrialLayer").setPointColor(p.color(255, 10, 10));
			plot.addLayer("frameLayer", pointsFrame);
			plot.getLayer("frameLayer").setPointColor(p.color(255, 255, 10));
			plot.addLayer("motorLayer", pointsMotor);
			plot.getLayer("motorLayer").setPointColor(p.color(10, 10, 255));
		plot.setYLim(0, 255);
		plot.getXAxis().setAxisLabelText("time (ms)");
		plot.getYAxis().setAxisLabelText("analog 0");
		plot.setTitleText("xxx");

		// Draw it!
		plot.defaultDraw();

		//p.noLoop();

		plot2 = new GPlot(p);
		plot2.setPos(25, 300);
		// Set the plot title and the axis labels
		plot2.setPoints(points);
		plot2.setXLim(0, 255);
		plot2.setYLim(0, 255);
		plot2.getXAxis().setAxisLabelText("time (ms)");
		plot2.getYAxis().setAxisLabelText("analog 1");
		plot2.setTitleText("xxx");
		// Draw it!
		plot2.defaultDraw();
	};

	p.draw = function() {
		// Clean the canvas
		p.background(255);

		plot.beginDraw();
		plot.drawBackground();
		plot.drawBox();
		plot.drawXAxis();
		plot.drawYAxis();
		plot.drawTitle();
		plot.drawGridLines(GPlot.BOTH);
		plot.drawLines();
		//plot.drawPoints(star);
		plot.drawPoints();
		plot.endDraw();

		plot2.beginDraw();
		plot2.drawBackground();
		plot2.drawBox();
		plot2.drawXAxis();
		plot2.drawYAxis();
		plot2.drawTitle();
		plot2.drawGridLines(GPlot.BOTH);
		//plot2.drawLines();
		//plot2.drawPoints(star);
		plot2.drawPoints();
		plot2.endDraw();
	}
	
	p.myupdate = function(serialData) {
		//15886,analogEvent,144,166
		res = serialData.trim().split(",");
		var event = res[1];
		var xMin = lastTrialStartMillis;
		var xMax = lastTrialStartMillis + 10000;
		if (event == "analogEvent") {
			pnt = new GPoint(res[0], res[2]);
			points.push(pnt);
			plot.setXLim(xMin,xMax); //last 10 seconds
			plot.setPoints(points);
		
			pnt = new GPoint(res[2], res[3]);
			points2.push(pnt);
			//plot2.setXLim(xMin,xMax); //last 10 seconds
			plot2.setPoints(points2);
		} else if (event == "startTrial") {
			lastTrialStartMillis = parseInt(res[0]);
			pnt = new GPoint(res[0], 100);
			pointsStart.push(pnt);
			plot.setXLim(xMin,xMax); //last 10 seconds
			plot.getLayer("startTrialLayer").setPoints(pointsStart);
			
		} else if (event == "stopTrial") {
			pnt = new GPoint(res[0], 100);
			pointsStop.push(pnt);
			plot.setXLim(xMin,xMax); //last 10 seconds
			plot.getLayer("stopTrialLayer").setPoints(pointsStop);
			
		} else if (event == "scanimageframe") {
			pnt = new GPoint(res[0], 100);
			pointsFrame.push(pnt);
			plot.setXLim(xMin,xMax); //last 10 seconds
			plot.getLayer("frameLayer").setPoints(pointsFrame);
			
		} else if ((event == "motorstart") || (event == "motorstop")) {
			pnt = new GPoint(res[0], 100);
			pointsMotor.push(pnt);
			plot.setXLim(xMin,xMax); //last 10 seconds
			plot.getLayer("motorLayer").setPoints(pointsMotor);
			
		} else {
			console.log("mygraphicaplot.js event not handled:" + event);
		}
	}
};
