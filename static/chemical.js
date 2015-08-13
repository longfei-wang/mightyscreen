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
 * ChemicalVis object
 * @param _parentElement -- the HTML or SVG element (D3 node) to which to attach the vis
 * @param _data -- the data array
 * @param _metaData -- the meta-data / data description object
 * @param _eventHandler -- the Eventhandling Object to emit data to (see Task 4)
 * @constructor
 */

ChemicalVis = function(_parentElement, _data, _eventHandler){
    this.parentElement = _parentElement;
    this.data = _data;
    this.eventHandler = _eventHandler;
    this.displayData = [];

    this.box = {width:125,height:180,outerwidth:145,outerheight:220};

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
    var that = this;

    //select molecules in selection
    this.displayData = $.extend({},this.data).results.filter(function(d){
            return d.hit == 1;
        });

    this.displayData.map(function(d){
        
        //put a lock on displayData do not visualize when data is not ready
        d.display = false;

        //read checmial property from pubchem
        $.get(d.identifier+'/JSON',function(dd){
            d.cid = dd.PC_Compounds[0].id.id.cid;
            dd.PC_Compounds[0].props.map(function(ddd){
                switch (ddd.urn.label) {
                    case 'Log P':
                        d.logp = ddd.value.fval;
                        break;
                    case 'Topological':
                        d.tpsa = ddd.value.fval;
                        break;
                    case 'Molecular Weight':
                        d.molecular_weight = ddd.value.fval;
                        break;
                }

            });

            d.display = true; //unlock it

            that.updateVis();

        }).error(function(){

            d.display = true;

            that.updateVis();
        });
    });

}


/**
 * the drawing function - should use the D3 selection, enter, exit
 * @param _options -- only needed if different kinds of updates are needed
 */
ChemicalVis.prototype.updateVis = function(){
    
    var that = this;

    //check the lock if it is lock then end function
    for (i in this.displayData) {
        if (this.displayData[i].display == false) {
            return;
        }
    }

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
    // this.symbol = this.svg
    //     .append("g")
    //     .attr("class", "symbol")
    //     .html(this.displayData.map(function(d) {return d.svg;}).join());

    this.svg.selectAll(".chemical").remove();

    this.chemical = this.svg.selectAll(".chemical")
        .data(this.displayData,function(d){return d.plate_well;})
        .enter()
        .append("g")
        .attr("class", "chemical")
        .attr("transform",function(d, i){ 
            return "translate("+ that.x(i % that.numCol) +","+  that.y(Math.floor(i/that.numCol))  +")";
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
    this.chemical.append("image")
        .attr("xlink:href", function(d) {return d.identifier+'/PNG?record_type=2d&image_size='+(that.box.width-2)+'x'+that.box.height*0.75; })
        .attr("width", this.box.width)
        .attr("height", this.box.height*0.75);

    var counter = 0;
    //the index
    this.chemical
        .append("text")
        .attr("y",14)
        .attr("x",2)
        .attr("anchor","left")
        .text(function(d) {
            if (d.hit) {
                counter += 1;
                return counter;
            }
    })

    //link to pubchem
    this.chemical
        .append("a")
        .attr("target","_blank")
        .attr("xlink:href",function(d){
            return 'https://pubchem.ncbi.nlm.nih.gov/compound/'+d.cid;
        })
        .append("text")
        .attr("class","hover_text")
        .attr("y",14)
        .attr("x",20)
        .attr("anchor","left")
        .text(function(d){
            return d.cid?"PubChem":"";
    });

    //link to close button
    this.chemical
        .append("text")
        .attr("y",14)
        .attr("x",this.box.width-15)
        .attr("anchor","right")
        .attr("class","hover_text")
        .text("X")
        .on("click",function(d){
        $(that.eventHandler).trigger("select",d.plate_well);
    });

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
        .attr("transform","translate("+(this.box.height*0.20+8)+","+5+")")
    mw.append("rect")
        .attr("width",this.box.height*0.20)
        .attr("height",this.box.height*0.20)
        .attr("style",function(d) {return "fill:" + (d.molecular_weight < 500 ? "orange":"white");})
    mw.append("text")
        .attr("x",5)
        .attr("y",15)
        .attr("anchor","left")
        .text(function(d) {return d.molecular_weight < 500 ? "MW" : "";});

    //if MW < 500 draw a rect
    var mw = p.append("g")
        .attr("transform","translate("+(this.box.height*0.40+12)+","+5+")")
    mw.append("rect")
        .attr("width",this.box.height*0.20)
        .attr("height",this.box.height*0.20)
        .attr("style",function(d) {return "fill:" + (d.tpsa < 140 ? "greenyellow":"white");})
    mw.append("text")
        .attr("x",5)
        .attr("y",15)
        .attr("anchor","left")
        .text(function(d) {return d.tpsa < 140 ? "tPSA" : "";});

    //after display is finished, lock the data
    // this.displayData.map(function(d){
    //     d.display = false;
    // });

}


/**
 * Gets called by event handler and should create new aggregated data
 * aggregation is done by the function "aggregate(filter)". Filter has to
 * be defined here.
 * @param selection
 */
ChemicalVis.prototype.onChemSelectionChange= function (plate_well){
    
    // TODO: call wrangle function
    
    this.data.results.map(function(d){
        if (d.plate_well==plate_well) {
            d.hit = 1 - d.hit;
        }
    });

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







