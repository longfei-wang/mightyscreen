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
 * PlateSelector object for HW3 of CS171
 * @param _parentElement -- the HTML or SVG element (D3 node) to which to attach the vis
 * @param _data -- the data array
 * @param _metaData -- the meta-data / data description object
 * @param _eventHandler -- the Eventhandling Object to emit data to (see Task 4)
 * @constructor
 */
PlateSelector = function(_parentElement, _data, _selection, _eventHandler){
    this.parentElement = _parentElement;
    this.data = _data;
    this.selection = _selection;
    this.eventHandler = _eventHandler;
    this.displayData = [];


    // TODO: define all "constants" here
    this.margin = {top: 20, right: 20, bottom: 20, left: 20},
    this.width = window.innerWidth - this.margin.left - this.margin.right,
    this.height = 100 - this.margin.top - this.margin.bottom;



    this.initVis();
}


/**
 * Method that sets up the SVG and the variables
 */
PlateSelector.prototype.initVis = function(){

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


    // filter, aggregate, modify data
    this.wrangleData();

    

    // call the update method
    this.updateVis();
}


/**
 * Method to wrangle the data. In this case it takes an options object
  */
PlateSelector.prototype.wrangleData= function(){

    // displayData should hold the data which is visualized
    // pretty simple in this case -- no modifications needed

}



/**
 * the drawing function - should use the D3 selection, enter, exit
 * @param _options -- only needed if different kinds of updates are needed
 */
PlateSelector.prototype.updateVis = function(){

    var that = this;
    // TODO: implement update graphs (D3: update, enter, exit)
    this.svg.selectAll(".plate").remove()

    this.plates = this.svg.selectAll(".plate")
        .data(this.data)
        .enter()
        .append("g")
        .attr("class","plate")
        .attr("transform", function(d,i){ return "translate("+ i*105 + ",0)"; });

    this.plates.append("rect")
        .attr("width",100)
        .attr("height",80)
        .attr("fill",function(d){ 
            return (d.key == that.selection) ? "red" : "grey";
        })
        .attr("fill-opacity",0.5)
        .on("click",function(d){
            $(that.eventHandler).trigger("plate",d.key);
        });

    this.plates.append("text")
        .attr("y",12)
        .text(function(d){ return d.key; });
}

/**
 * Gets called by event handler and should create new aggregated data
 * aggregation is done by the function "aggregate(filter)". Filter has to
 * be defined here.
 * @param selection
 */
PlateSelector.prototype.onSelectionChange= function (selectionStart, selectionEnd){

    // TODO: call wrangle function

    // do nothing -- no update when brushing

}


PlateSelector.prototype.onPlateChange= function (p){

    // TODO: call wrangle function
    this.selection = p;

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











