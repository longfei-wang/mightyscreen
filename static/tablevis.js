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

    // this.filter = this.parentElement.append("input")
    //         .attr("class","form-control");

    // this.pagination = this.parentElement.append("ul")
    //         .attr("class","pagination");

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
    this.displayData = this.data.results.map(function(d){
        
        var welltype = '<label class="radio-inline">' +
        '<input type="radio" pw="'+d.plate_well+'" name="welltype'+d.plate_well+'" value="X" '+(d.welltype=='X'?'checked':'')+'>X</label>'+
        '<label class="radio-inline">'+
        '<input type="radio" pw="'+d.plate_well+'" name="welltype'+d.plate_well+'" value="P" '+(d.welltype=='P'?'checked':'')+'>P</label>'+
        '<label class="radio-inline">'+
        '<input type="radio" pw="'+d.plate_well+'" name="welltype'+d.plate_well+'" value="N" '+(d.welltype=='N'?'checked':'')+'>N</label>';
        d.welltype = welltype;

        var hit = '<input type="checkbox" name="hit" value="'+d.plate_well+'" '+(d.hit==1?'checked':'')+'>';
        
        d.hit = hit;

        var identifier = '<a href="'+d.identifier+'/PNG">'+'LINK'+'</a>';

        d.identifier = identifier;

        delete d.plate;
        delete d.plate_well;
        
        return d;
    });
    this.plateList = this.data.plateList;
    this.curPlate = this.data.curPlate;

    //trim

}

/**
 * the drawing function - should use the D3 selection, enter, exit
 * @param _options -- only needed if different kinds of updates are needed
 */
TableVis.prototype.updateVis = function(){

    var that = this;
    // update the table header
    var columns = Object.keys(this.displayData[0]);
    
    var sortorder = -1;


    var header = this.thead.selectAll("th")
        .data(columns)
        
    

    header.enter()
        .append("th")
        .text(function(d) { return d.substring(0,30); })
        .on("click", function(header, i) {
          
          sortorder = - sortorder;
          that.tbody.selectAll("tr").sort(function(a, b) {
            //sort function that use name as secondary sort.
            return sortorder * (a[header] == b[header] ? d3.descending(a['plate_well'],b['plate_well'])  : d3.descending(a[header], b[header]));
          });
        });

    header.exit().remove();

    // update the table content

    this.tbody.selectAll("tr.tablevisrow").remove()

    var rows = this.tbody.selectAll("tr.tablevisrow").data(this.displayData, function(d) {return d.well;});

    rows.enter()
        .append("tr")
        .attr("class", "tablevisrow");
    rows.exit().remove();
    
    var cells = rows.selectAll("td")
        .data(function(row){
        return d3.values(row);
    });

    cells.enter().append("td")
    cells.html(function(d,i) {
        return d;

    });
    cells.exit().remove();

    d3.selectAll('input[name="hit"]').on('click',function(){
        
        var plate_well = $(this).val();

        $(that.eventHandler).trigger("hit",plate_well);
    });

    d3.selectAll('input[type="radio"]').on('click',function(){
        
        var welltype = $(this).val();
        var plate_well = $(this).attr('pw');
        $(that.eventHandler).trigger("welltype",[plate_well,welltype]);
    });

}


/**
 * Gets called by event handler and should create new aggregated data
 * aggregation is done by the function "aggregate(filter)". Filter has to
 * be defined here.
 * @param selection
 */

TableVis.prototype.onPlateChange= function (d){


    // TODO: call wrangle function
    this.data = d;

    this.wrangleData();

    this.updateVis();
    // do nothing -- no update when brushing
}

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
