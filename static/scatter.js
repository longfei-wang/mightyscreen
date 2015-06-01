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
 * ScatterVis object for HW3 of CS171
 * @param _parentElement -- the HTML or SVG element (D3 node) to which to attach the vis
 * @param _data -- the data array
 * @param _metaData -- the meta-data / data description object
 * @param _eventHandler -- the Eventhandling Object to emit data to (see Task 4)
 * @constructor
 */
ScatterVis = function(_parentElement, _data, _channelx, _channely, _eventHandler){
    this.parentElement = _parentElement;
    this.data = _data;
    this.channelx = _channelx;
    this.channely = _channely;
    this.eventHandler = _eventHandler;
    this.displayData = [];
    

    // TODO: define all "constants" here
    this.margin = {top: 20, right: 20, bottom: 50, left: 80},
    this.width = 720 - this.margin.left - this.margin.right,
    this.height = 480 - this.margin.top - this.margin.bottom;



    this.initVis();
}


/**
 * Method that sets up the SVG and the variables
 */
ScatterVis.prototype.initVis = function(){

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

    this.logp = d3.scale.linear()
        .domain([-6,20]).range([10,0]);

    this.mw = d3.scale.linear()
        .domain([0,2000]).range([10,0]);

    this.wt = {
        "P" : "red",
        "N" : "green",
        "X" : "blue",
        "E" : "white",
        "B" : "white"
    }

    this.xAxis = d3.svg.axis()
        .scale(this.x)
        .tickFormat(this.format)
        .orient("bottom");

    this.yAxis = d3.svg.axis()
        .scale(this.y)
        .tickFormat(this.format)
        .orient("left");

    this.svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + this.height + ")")

    this.svg.append("g")
        .attr("class", "y axis");

    //labels for x and y axis
    this.svg.append("text")
        .attr("id","ylabel")
        .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
        .attr("transform", "translate("+ (-40) +","+(this.height/2)+")rotate(-90)")  // text is drawn off the screen top left, move down and out and rotate
        .text("Channel 2 Readout: "+this.channely);

    this.svg.append("text")
        .attr("id","xlabel")
        .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
        .attr("transform", "translate("+ (this.width/2) +","+(this.height+45)+")")  // centre below axis
        .text("Channel 1 Readout: "+this.channelx);



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
ScatterVis.prototype.wrangleData= function(_filter){

    // displayData should hold the data which is visualized
    // pretty simple in this case -- no modifications needed
    that = this;

    var filter = function(){return true;}
    if (_filter != null){
        filter = _filter;
    }

    var filtered_data = this.data.filter(filter);

    var data = filtered_data.map(function(d) {
        return  {"platewell": d.platewell,
                "fpA": d.fpA,
                "fpB": d.fpB,
                "fiA": d.fiA,
                "fiB": d.fiB,
                "logp":d.logp,
                "wt":d.welltype,
                "mw":d.mw,};
    });

    //set domain for scales

    this.x.domain(d3.extent(this.data.map(function(d){ return d[that.channelx]; })))

    this.y.domain(d3.extent(this.data.map(function(d) {return d[that.channely]; })));

    //this.wt.domain(d3.extent(data.map(function(d) {return d.wt; })));

    this.displayData = data;

}



/**
 * the drawing function - should use the D3 selection, enter, exit
 * @param _options -- only needed if different kinds of updates are needed
 */
ScatterVis.prototype.updateVis = function(){

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

    this.svg.selectAll(".dot").remove();
    // updates graph
    this.dot = this.svg.selectAll(".dot")
        .data(this.displayData)
        .enter()
        .append("g")
        .attr("class","dot")
        .attr("transform",function(d) {
            return "translate ("+ that.x(d[that.channelx]) + "," + that.y(d[that.channely]) + ")";
        });

    //color encode welltype size encode drug-like property
    this.dot.append("circle")
        .attr("fill", function(d) {return that.wt[d.wt]; })
        .attr("fill-opacity",0.2)
        .attr("stroke","grey")
        //.attr("stroke-width", function(d) {return d.mw ? that.mw(d.mw) : 0;})
        .attr("stroke-opacity",0.2)
        .attr("r",10)
        .on("click",function(d) {
            $(that.eventHandler).trigger("select",d.platewell);
        });

    //this.dots.exit().remove();

}

/**
 * Gets called by event handler and should create new aggregated data
 * aggregation is done by the function "aggregate(filter)". Filter has to
 * be defined here.
 * @param selection
 */
ScatterVis.prototype.onSelectionChange= function (selection){

    // TODO: call wrangle function
    this.wrangleData(function(d) {
        var flag = true;
        Object.keys(selection).map(function(k) {
            flag = (d[k] >= selection[k][0]) && (d[k] <= selection[k][1]) && flag
        });
        return flag;
    });

    this.updateVis();
    // do nothing -- no update when brushing

}

ScatterVis.prototype.onPlateChange= function (d){


    // TODO: call wrangle function
    this.data = d;

    this.wrangleData();

    this.updateVis();
    // do nothing -- no update when brushing

}

ScatterVis.prototype.onChannelChange= function (c1,c2){


    // TODO: call wrangle function
    this.channelx = c1;
    
    this.channely = c2;

    this.parentElement.select("#xlabel")
        .text("Channel 1 Readout: "+this.channelx);
    
    this.parentElement.select("#ylabel")
        .text("Channel 2 Readout: "+this.channely);
    
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
ScatterVis.prototype.addSlider = function(svg){
    var that = this;

    // TODO: Think of what is domain and what is range for the y axis slider !!
    var sliderScale = d3.scale.linear().domain([0.1,1]).range([0,this.height])

    var sliderDragged = function(){
        var value = Math.max(0, Math.min(200,d3.event.y));

        var sliderValue = sliderScale.invert(value);

        // TODO: do something here to deform the y scale
        //console.log("Y Axis Slider value: ", sliderValue);
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






