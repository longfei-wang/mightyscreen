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
 * ChemicalVis object for final project of CS171
 * @param _parentElement -- the HTML or SVG element (D3 node) to which to attach the vis
 * @param _data -- the data array
 * @param _metaData -- the meta-data / data description object
 * @param _eventHandler -- the Eventhandling Object to emit data to (see Task 4)
 * @constructor
 */

ChemicalVis = function(_parentElement, _data, _eventHandler){
    this.parentElement = _parentElement;
    this.data = _data;
    this.selection = [];
    this.eventHandler = _eventHandler;
    this.displayData = [];

    this.box = {width:125,height:200,outerwidth:145,outerheight:220};

    // TODO: define all "constants" here
    this.margin = {top: 20, right: 200, bottom: 20, left: 20},
    this.width = window.innerWidth - this.margin.left - this.margin.right,
    this.height = 0;

    this.numRow = 0;
    this.numCol = Math.floor(this.width / this.box.outerwidth);

    this.initVis();
}


/**
 * Method that sets up the SVG and the variables
 */
ChemicalVis.prototype.initVis = function(){

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
        .attr("width", this.width)
        .attr("height", this.height)
      .append("g")
        .attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");




    // filter, aggregate, modify data
    this.wrangleData();

    // call the update method
    this.updateVis();
}


/**
 * Method to wrangle the data. In this case it takes an options object
  */
ChemicalVis.prototype.wrangleData= function(){

    // displayData should hold the data which is visualized
    // pretty simple in this case -- no modifications needed
    // A certain propety will be used here. As an example we use fpA
    that = this;

    //select molecules in selection
    var filtered = this.data.filter(function(d) {return d.svg && (that.selection.indexOf(d.platewell) > -1) ;});

    this.displayData = filtered.sort(function(a,b) {
        return d3.ascending(that.selection.indexOf(a.platewell),that.selection.indexOf(b.platewell)); 
    });

}



/**
 * the drawing function - should use the D3 selection, enter, exit
 * @param _options -- only needed if different kinds of updates are needed
 */
ChemicalVis.prototype.updateVis = function(){

    // TODO: implement update graphs (D3: update, enter, exit)

    this.numRow = Math.ceil(this.displayData.length / this.numCol);

    this.height = this.numRow * this.box.outerheight + (this.numRow ? this.margin.bottom : 0);

    this.parentElement.select("svg").attr("height", this.height);

    // creates axis and scales
    this.x = d3.scale.linear()
        .domain([0, this.numCol])
        .range([0, this.width]);

    this.y = d3.scale.linear()
        .domain([0, this.numRow])
        .range([0, this.height]);

    //add symbols (svg reference)
    this.symbol = this.svg
        .append("g")
        .attr("class", "symbol")
        .html(this.displayData.map(function(d) {return d.svg;}).join());

    this.svg.selectAll(".chemical").remove();

    this.chemical = this.svg.selectAll(".chemical")
        .data(this.displayData,function(d){return d.platewell;})
        .enter()
        .append("g")
        .attr("class", "chemical")
        .attr("transform",function(d, i){ 
            return "translate("+ that.x(i % that.numCol) +","+  that.y(Math.floor(i/that.numCol))  +")";
        })
        .on("click",function(d){
            $(that.eventHandler).trigger("select",d.platewell);
        });
    
    //shadow
    this.chemical.append("rect")
        .attr("x",5)
        .attr("y",5)
        .attr("width",this.box.width)
        .attr("height",this.box.height)
        .attr("style","fill:grey");

    //draw top box
    this.chemical.append("rect")
        .attr("width",this.box.width)
        .attr("height",this.box.height*0.75)
        .attr("style","fill:white;stroke:black;");

    //draw chemical
    this.chemical.append("use")
        .attr("xlink:href", function(d) {return "#sym"+d.platewell; })
        .attr("width", this.box.width)
        .attr("height", this.box.height*0.75);

    //the index
    this.chemical.append("text")
        .attr("y",14)
        .attr("x",2)
        .attr("anchor","left")
        .text(function(d) {return that.selection.indexOf(d.platewell)+1;})

    //the bottom box
    var p = this.chemical.append("g")
        .attr("transform","translate("+0+","+this.box.height*0.75+")")
    
    p.append("rect")
        .attr("width",this.box.width)
        .attr("height",this.box.height*0.25)
        .attr("style","fill:white;stroke:black;")

    //if logP < 5 draw a rect
    var logp = p.append("g")
        .attr("transform","translate("+5+","+5+")")

    logp.append("rect")
        .attr("width",this.box.height*0.20)
        .attr("height",this.box.height*0.20)
        .attr("style",function(d) {return "fill:" + (d.logp < 5 ? "cyan":"white");})
    logp.append("text")
        .attr("x",5)
        .attr("y",15)
        .attr("anchor","left")
        .text(function(d) {return d.logp < 5 ? "logP" : "";})

    //if MW < 500 draw a rect
    var mw = p.append("g")
        .attr("transform","translate("+(this.box.height*0.20+10)+","+5+")")
    mw.append("rect")
        .attr("width",this.box.height*0.20)
        .attr("height",this.box.height*0.20)
        .attr("style",function(d) {return "fill:" + (d.mw < 500 ? "orange":"white");})
    mw.append("text")
        .attr("x",5)
        .attr("y",15)
        .attr("anchor","left")
        .text(function(d) {return d.mw < 500 ? "MW" : "";});
}

/**
 * Gets called by event handler and should create new aggregated data
 * aggregation is done by the function "aggregate(filter)". Filter has to
 * be defined here.
 * @param selection
 */
ChemicalVis.prototype.onChemSelectionChange= function (_selection){
    
    // TODO: call wrangle function
    this.selection=_selection;



    this.wrangleData();

    this.updateVis();

    // do nothing -- no update when brushing

}

ChemicalVis.prototype.onPlateChange= function (d){


    // TODO: call wrangle function
    this.data = d;

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









