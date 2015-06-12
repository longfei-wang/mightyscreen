/**
 * Author Longfei Wang 5/24/2015.
 * Based on template Created by Hendrik Strobelt (hendrik.strobelt.com) on 1/28/15.
 */


/*
 *
 * ======================================================
 * We follow the vis template of init - wrangle - update
 * ======================================================
 *
 * */

/**
 * TableVis object
 * @param _parentElement -- the HTML or SVG element (D3 node) to which to attach the vis
 * @param _data -- the data array
 * @param _metaData -- the meta-data / data description object
 * @param _eventHandler -- the Eventhandling Object to emit data to (see Task 4)
 * @constructor
 */
TableVis = function(_parentElement, _data, _eventHandler){
    
    this.parentElement = _parentElement;
    this.eventHandler = _eventHandler;
    this.displayData = [];
    this.query = {};
    this.data = _data;
    this.plateList = [];
    this.curPlate = null;
    this.table = null;
    this.thead = null;
    this.tbody = null;
    this.filter = null;
    this.pagination = null;

    // TODO: define all "constants" here
    this.initVis();
}


/**
 * Method that sets up the SVG and the variables
 */
TableVis.prototype.initVis = function(){

    var that = this; // read about the this

    this.filter = this.parentElement.append("input")
            .attr("class","form-control");

    this.pagination = this.parentElement.append("ul")
            .attr("class","pagination");

    table = this.parentElement.append("table")
            .attr("class","table");
    
    table.append("caption").html('TableView');

    this.thead = table.append("thead")
            .attr("class", "thead")
            .append("tr");

    this.tbody = table.append("tbody");

    this.wrangleData();
    this.updateVis();

}


/**
 * Method to wrangle the data. In this case it takes an options object
  */
TableVis.prototype.wrangleData= function(){

    // displayData should hold the data which is visualized
    // pretty simple in this case -- no modifications needed
    this.displayData = this.data.results;
    this.plateList = this.data.plateList;
    this.curPlate = this.data.curPlate;

    //trim

}

/**
 * the drawing function - should use the D3 selection, enter, exit
 * @param _options -- only needed if different kinds of updates are needed
 */
TableVis.prototype.updateVis = function(){

    var that = this
    // update the table header
    var columns = Object.keys(this.displayData[0]);

    this.pagination.append("li")
        .append("a")
        .text("asdfsdf")

    var header = this.thead.selectAll("th")
        .data(columns)
        
    header.enter()
        .append("th")
        .text(function(d) { return that.data.verbose[d] ? that.data.verbose[d] : d; })
        .on("click",function(d){
            that.query.ordering = that.query.ordering == d ? ('-' + d) : d;
            $(that.eventHandler).trigger('query',that.query);
        });

    header.exit().remove();

    // update the table content

    this.tbody.selectAll("tr.tablevisrow").remove()

    var rows = this.tbody.selectAll("tr.tablevisrow").data(this.displayData, function(d) {return d.plate_well;});

    rows.enter()
        .append("tr")
        .attr("class", "tablevisrow");
    rows.exit().remove();
    
    var cells = rows.selectAll("td")
        .data(function(row){
        return d3.values(row);
    });

    cells.enter().append("td")
    cells.text(function(d) {return d; });
    cells.exit().remove();

    this.parentElement.append('div')
}


/**
 * Gets called by event handler and should create new aggregated data
 * aggregation is done by the function "aggregate(filter)". Filter has to
 * be defined here.
 * @param selection
 */
TableVis.prototype.onQuery= function (d){

    this.data = d;
    this.wrangleData();
    this.updateVis();

}

/*
 *
 * ==================================
 * From here on only HELPER functions
 * ==================================
 *
 * */
