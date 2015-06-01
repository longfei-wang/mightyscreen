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
TableVis = function(_parentElement, _baseUrl, _eventHandler){
    
    this.parentElement = _parentElement;
    this.eventHandler = _eventHandler;
    this.baseUrl = _baseUrl;
    this.displayData = [];
    this.query = {};
    this.data = {};

    this.thead = null;
    this.tbody = null;

    // TODO: define all "constants" here
    this.initVis();
}


/**
 * Method that sets up the SVG and the variables
 */
TableVis.prototype.initVis = function(){

    var that = this; // read about the this

    var table = this.parentElement.append("table")
            .attr("class","table");
    
    table.append("caption").html('TableView');

    this.thead = table.append("thead")
            .attr("class", "thead")
            .append("tr");

    this.tbody = table.append("tbody");

    this.refreshTable();
}


/**
 * Method to wrangle the data. In this case it takes an options object
  */
TableVis.prototype.wrangleData= function(){

    // displayData should hold the data which is visualized
    // pretty simple in this case -- no modifications needed
    this.displayData = this.data.results;


}

/**
 * the drawing function - should use the D3 selection, enter, exit
 * @param _options -- only needed if different kinds of updates are needed
 */
TableVis.prototype.updateVis = function(){

    // update the table header
    var columns = Object.keys(this.displayData[0]);

    var sortorder = -1;

    var header = this.thead.selectAll("th")
        .data(columns)
        
    header.enter()
        .append("th")
        .text(function(d) { return d; });

    header.exit().remove();

    // update the table content 
    var rows = this.tbody.selectAll("tr.tablevisrow").data(this.displayData, function(d) {return d.plate_well;});

    rows.enter()
        .append("tr")
        .attr("class", "tablevisrow");
    rows.exit().remove();
    
    var cells = rows.selectAll("td")
        .data(function(row){
        console.log(d3.values(row));return d3.values(row);
    });

    cells.enter().append("td")
    cells.text(function(d) {return d; });
    cells.exit().remove();

}


TableVis.prototype.refreshTable= function (){
    var that = this;

    $.get(this.baseUrl,
        this.query,
        function(data) {
            console.log(data);
            that.data = data;
            that.wrangleData();
            that.updateVis();
    });

}
/**
 * Gets called by event handler and should create new aggregated data
 * aggregation is done by the function "aggregate(filter)". Filter has to
 * be defined here.
 * @param selection
 */
TableVis.prototype.onPlateChange= function (plate){

    this.query.plate = plate;
    this.refreshTable();

}



/*
 *
 * ==================================
 * From here on only HELPER functions
 * ==================================
 *
 * */
