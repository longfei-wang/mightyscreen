/**
 * Created by Longfei Wang on 5/4/15.
 */


/*
 *
 * ======================================================
 * We follow the vis template of init - wrangle - update
 * ======================================================
 *
 * */

/**
 * PlateSelector object
 * @param _parentElement -- the HTML or SVG element (D3 node) to which to attach the vis
 * @param _data -- the data array
 * @param _metaData -- the meta-data / data description object
 * @param _eventHandler -- the Eventhandling Object to emit data to (see Task 4)
 * @constructor
 */
PlateSelector = function(_parentElement, _data, _eventHandler){
    this.parentElement = _parentElement;
    this.data = _data.plateList;
    this.data_slice = [];
    this.curPlate = _data.curPlate;
    this.curRow = 0;
    this.eventHandler = _eventHandler;
    this.displayData = [];
    // TODO: define all "constants" here
    this.margin = {top: 20, right: 20, bottom: 20, left: 20},
    this.width = window.innerWidth - this.margin.left - this.margin.right,
    this.height = 110 - this.margin.top - this.margin.bottom;

    this.box = {height:70,width:100,space:105};

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

    this.x = d3.scale.linear()
        .range([5, this.width]);

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

    //slice the data.
    var that = this;

    this.platesRow = Math.floor(this.width/this.box.space);
    
    this.numRow = Math.ceil(this.data.length/this.platesRow);
    

    for (i=0;i<this.numRow;i++) {
        var slice = that.data.slice(that.platesRow*i,that.platesRow*(i+1));    
        that.data_slice.push(slice);
        slice.map(function(d){
            if (d.plate == parseInt(that.curPlate)) {
                that.curRow = i;
            }
        });
    }


    this.x.domain([0, Math.floor(this.width/15)]);
    
    this.displayData = this.data_slice[this.curRow];
}



/**
 * the drawing function - should use the D3 selection, enter, exit
 * @param _options -- only needed if different kinds of updates are needed
 */
PlateSelector.prototype.updateVis = function(){

    var that = this;
    // TODO: implement update graphs (D3: update, enter, exit)
    this.svg.selectAll(".plate").remove()

    this.dots = this.svg.append('g')
        .selectAll(".dot")
        .data(d3.range(0,this.numRow))
        .enter()
        .append("circle")
        .attr("class","dot hover_item")
        .attr("cx",function(d) {return that.x(d);})
        .attr("cy",this.box.height+10)
        .attr("r",5)
        .attr('fill',function(d){return d==that.curRow ? 'red':'grey';})
        .on('click',function(d){
            that.curRow = d;
            that.displayData=that.data_slice[d];
            that.updateVis(); 
        });

    this.plates = this.svg.selectAll(".plate")
        .data(this.displayData,function(d){return d.plate;})
        .enter()
        .append("g")
        .attr("class","plate hover_item")
        .attr("transform", function(d,i){ return "translate("+ i*that.box.space + ",0)"; });

    this.plates.append("rect")
        .attr("width",this.box.width)
        .attr("height",this.box.height)
        .attr("fill",function(d){ 
            return (d.plate == parseInt(that.curPlate)) ? "red" : "grey";
        })
        .attr("fill-opacity",0.5)
        .on("click",function(d){
            $(that.eventHandler).trigger("plate",d.plate);
        });

    this.plates.append("text")
        .attr("y",12)
        .text(function(d){ return d.plate; });

    this.plates.append("text")
        .attr("y",40)
        .attr("x",this.box.width-5)
        .attr("text-anchor","end")
        .attr("fill","purple")
        .text(function(d){ return d.numHit; });

    this.plates.append("text")
        .attr("y",this.box.height-2)
        .attr("fill","white")
        .text(function(d){ return d.date.split("T")[0]; });
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
    this.curPlate = p;

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











