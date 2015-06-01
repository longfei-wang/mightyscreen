/**
 * Created by Hendrik Strobelt (hendrik.strobelt.com) on 1/28/15.
 */


/*
 *
 * ======================================================
 * We follow the vis template of init - wrangle - update
 * ======================================================
 *
 * */

/**
 * DistVis object for HW3 of CS171
 * @param _parentElement -- the HTML or SVG element (D3 node) to which to attach the vis
 * @param _data -- the data array
 * @param _metaData -- the meta-data / data description object
 * @param _eventHandler -- the Eventhandling Object to emit data to (see Task 4)
 * @constructor
 */
DistVis = function(_parentElement, _data, _channel, _eventHandler){
    this.parentElement = _parentElement;
    this.data = _data;
    this.channel = _channel;
    this.eventHandler = _eventHandler;
    this.displayData = [];
    this.bins = 100;
    this.controls = [];
    

    // TODO: define all "constants" here
    this.margin = {top: 20, right: 20, bottom: 50, left: 80},
    this.width = 700 - this.margin.left - this.margin.right,
    this.height = 150 - this.margin.top - this.margin.bottom;

    this.initVis();
}


/**
 * Method that sets up the SVG and the variables
 */
DistVis.prototype.initVis = function(){

    var that = this; // read about the this

    //TODO: implement here all things that don't change
    //TODO: implement here all things that need an initial status
    // Examples are:
    // - construct SVG layout
    // - create axis
    // -  implement brushing !!
    // --- ONLY FOR BONUS ---  implement zooming

    // TODO: modify this to append an svg element, not modify the current placeholder SVG element
    this.svg = this.parentElement.append("svg")
        .attr("width", this.width + this.margin.left + this.margin.right)
        .attr("height", this.height + this.margin.top + this.margin.bottom)
      .append("g")
        .attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");

    // creates axis and scales
    this.format = d3.format("s");

    this.x = d3.scale.linear()
        .range([0, this.width]);

    this.y = d3.scale.pow()
        .range([this.height, 0]);

    this.xAxis = d3.svg.axis()
        .scale(this.x)
        .tickFormat(this.format)
        .orient("bottom");

    this.yAxis = d3.svg.axis()
        .scale(this.y)
        .tickFormat(this.format)
        .orient("left");

    this.area = d3.svg.area()
        .interpolate("monotone")
        .x(function(d) { return that.x(d.x); })
        .y0(this.height)
        .y1(function(d) { return that.y(d.y); });


    this.brush = d3.svg.brush()
        .on("brush", function(){
        // Trigger selectionChanged event. You'd need to account for filtering by time AND type
        e = that.brush.extent();
        $(that.eventHandler).trigger("brush",[e[0],e[1],that.channel]);
        
        });
    
    this.svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + this.height + ")")


    this.svg.append("g")
        .attr("class", "y axis");

    //labels for x and y axis
    this.svg.append("text")
        .attr("text-anchor", "middle")  
        .attr("transform", "translate("+ (-35) +","+(this.height/2)+")rotate(-90)")  
        .text("Counts");

    this.svg.append("text")
        .attr("id","xlabel")
        .attr("text-anchor", "middle")
        .attr("transform", "translate("+ (this.width/2) +","+(this.height+45)+")")  
        .text("Selected Readout: "+this.channel);


    this.svg.append("g")
        .attr("class","brush");

    //TODO: implement the slider -- see example at http://bl.ocks.org/mbostock/6452972
    //this.addSlider(this.svg)


    // filter, aggregate, modify data
    this.wrangleData();

    // call the update method
    this.updateVis();
}


/**
 * Method to wrangle the data. In this case it takes an options object
  */
DistVis.prototype.wrangleData= function(){

    // displayData should hold the data which is visualized
    // pretty simple in this case -- no modifications needed
    that = this;

    var data = this.data.map(function(d) {
        return  d[that.channel];
    });

    this.controls = this.data.filter(function(d){return d.welltype == "P" || d.welltype == "N"; });
    //set domain for scales

    this.x.domain(d3.extent(data))

    var histogram = d3.layout.histogram()
        .bins(this.x.ticks(that.bins))
        (data);

    this.y.domain(d3.extent(histogram.map(function(d) {return d.y;})));

    this.displayData = histogram;

}



/**
 * the drawing function - should use the D3 selection, enter, exit
 * @param _options -- only needed if different kinds of updates are needed
 */
DistVis.prototype.updateVis = function(){

    // TODO: implement update graphs (D3: update, enter, exit)


    // updates axis
    this.svg.select(".x.axis")
        .call(this.xAxis)
        .selectAll("text")  
        .style("text-anchor", "end")
        .attr("dy", ".35em")
        .attr("transform", "translate(-5,5) rotate(-60)");


    this.svg.select(".y.axis")
        .call(this.yAxis)

    //draw all the controls
    var controls = this.svg.selectAll(".controls")
        .data(this.controls,function(d){return d.platewell;});

    controls.enter()
        .append("line")
        .attr("class","controls")
        .attr("x1",function(d) {return that.x(d[that.channel]); })
        .attr("x2",function(d) {return that.x(d[that.channel]); })
        .attr("y1",0)
        .attr("y2",this.height)
        .attr("style",function(d) {
            return "stroke:"+(d.welltype=="P" ? "red" : "green") +";stroke-width:1;stroke-opacity:0.3";
        });

    controls.exit().remove();

    // updates graph
    var path = this.svg.selectAll(".area")
      .data([this.displayData])

    path.enter()
      .append("path")
      .attr("class", "area")
      .style("opacity",0.6);

    path
      .transition()
      .attr("d", this.area);

    path.exit()
      .remove();

    this.brush.x(this.x);

    this.svg.select(".brush")
        .call(this.brush)
        .selectAll("rect")
        .attr("height", this.height);

}

/**
 * Gets called by event handler and should create new aggregated data
 * aggregation is done by the function "aggregate(filter)". Filter has to
 * be defined here.
 * @param selection
 */
DistVis.prototype.onSelectionChange= function (selectionStart, selectionEnd){

    // TODO: call wrangle function

    // do nothing -- no update when brushing

}


DistVis.prototype.onPlateChange= function (d){


    // TODO: call wrangle function
    this.data = d;

    this.brush.clear();

    this.wrangleData();

    this.updateVis();
    // do nothing -- no update when brushing

}

DistVis.prototype.onChannelChange= function (c){


    // TODO: call wrangle function
    this.channel = c;
    
    this.parentElement.select("#xlabel")
        .text("Selected Readout: "+this.channel);

    this.wrangleData();

    this.updateVis();
    // do nothing -- no update when brushing

}
/*
 *
 * ==================================
 * From here on only HELPER functions
 * ==================================
 *
 * */





/**
 * creates the y axis slider
 * @param svg -- the svg element
 */
DistVis.prototype.addSlider = function(svg){
    var that = this;

    // TODO: Think of what is domain and what is range for the y axis slider !!
    var sliderScale = d3.scale.linear().domain([0.1,1]).range([0,this.height])

    var sliderDragged = function(){
        var value = Math.max(0, Math.min(200,d3.event.y));

        var sliderValue = sliderScale.invert(value);

        // TODO: do something here to deform the y scale
        that.y.exponent(sliderValue);

        d3.select(this)
            .attr("y", function () {
                return sliderScale(sliderValue);
            })

        that.updateVis({});
    }
    var sliderDragBehaviour = d3.behavior.drag()
        .on("drag", sliderDragged)

    var sliderGroup = svg.append("g").attr({
        class:"sliderGroup",
        "transform":"translate(-70,30)"
    })

    sliderGroup.append("rect").attr({
        class:"sliderBg",
        x:5,
        width:10,
        height:200
    }).style({
        fill:"lightgray"
    })

    sliderGroup.append("rect").attr({
        "class":"sliderHandle",
        y:200,
        width:20,
        height:10,
        rx:2,
        ry:2
    }).style({
        fill:"#333333"
    }).call(sliderDragBehaviour)


}






