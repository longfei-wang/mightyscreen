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
 * CloudVis object for final project of CS171
 * @param _parentElement -- the HTML or SVG element (D3 node) to which to attach the vis
 * @param _data -- the data array
 * @param _metaData -- the meta-data / data description object
 * @param _eventHandler -- the Eventhandling Object to emit data to (see Task 4)
 * @constructor
 */

CloudVis = function(_parentElement, _data, _channel, _reverse, _eventHandler){
    this.parentElement = _parentElement;
    this.data = _data;
    this.channel = _channel;
    this.reverse = _reverse;
    this.eventHandler = _eventHandler;
    this.displayData = [];


    // TODO: define all "constants" here
    this.margin = {top: 20, right: 20, bottom: 20, left: 20},
    this.width = 720 - this.margin.left - this.margin.right,
    this.height = 480 - this.margin.top - this.margin.bottom;


    this.initVis();
}


/**
 * Method that sets up the SVG and the variables
 */
CloudVis.prototype.initVis = function(){

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

    // filter, aggregate, modify data
    this.wrangleData();
    this.nodes = this.displayData;

    // creates axis and scales
    this.scale = d3.scale.linear()
        .domain(d3.extent(this.nodes, function(d) { return d.readout; }))
    
    if (this.reverse) {
        this.scale.range([(this.width+this.height) / 5, 0]);
    }else {
        this.scale.range([0, (this.width+this.height) / 5]);
    }
    //set the radius and inital positions
    this.displayData.map(function(d) {
        res = d;
        // res.x = (Math.random() - 0.5) * 200 + that.width / 2, 
        // res.y = (Math.random() - 0.5) * 200 + that.height /2,
        res.radius  = that.scale(res.readout) / 2 ;
        return res; 
    });

    //start the force layout
    this.force = d3.layout.force()
        .size([this.width,this.height])
        .charge(0)
        .gravity(0.05)
        .nodes(this.nodes)
        .start();

    //set ticks
    this.force.on("tick", function(e) {
        var q = d3.geom.quadtree(that.nodes),
            i = 0,
            n = that.nodes.length;

        while (++i < n) q.visit(that.collide(that.nodes[i]));

            that.svg.selectAll(".node")
              .attr("transform", function(d) { return "translate("+d.x+","+d.y+")";  })
    });

    //add symbols (svg reference)
    this.symbol = this.svg
        .append("g")
        .attr("class", "symbol")
        .html(this.displayData.map(function(d) {return d.svg;}).join());

    this.node = this.svg.selectAll(".node")
        .data(this.displayData)
        .enter()
        .append("g")
        .attr("class", "node")
        .attr("transform",function(d){ 
            return "translate("+d.x+","+d.y+")";
        })
        .call(this.force.drag);
    
    //This is the "handle" of molecules looks ugly can be improved
    this.node.append("circle")
        .attr("fill","grey")
        .attr("fill-opacity",0.2)
        .attr("r",function(d) {return that.scale(d.readout) / 20;})

    //the collision box... doesn't work
    // this.node.append("rect")
    //     .attr("height",function(d) {return that.scale(d.readout); })
    //     .attr("width",function(d) {return that.scale(d.readout); });

    this.node.append("use")
      .attr("xlink:href", function(d) {return "#sym"+d.platewell; })
      .attr("width", function(d) {return that.scale(d.readout); })
      .attr("height", function(d) {return that.scale(d.readout); });


    // call the update method
    this.updateVis();
}


/**
 * Method to wrangle the data. In this case it takes an options object
  */
CloudVis.prototype.wrangleData= function(){

    // displayData should hold the data which is visualized
    // pretty simple in this case -- no modifications needed
    // A certain propety will be used here. As an example we use fpA
    that = this;
    var filtered = this.data.filter(function(d) {return d.svg || 0 ;})

    var data = filtered.map(function(d) {
        return  {'platewell':d.platewell,
                'svg':d.svg,
                'readout':d[that.channel],
            };
    });

    data = data.sort(function(a,b) {
        return that.reverse ?  d3.ascending(a.readout,b.readout) : d3.descending(a.readout,b.readout); });

    this.displayData = data.slice(0,50);

}



/**
 * the drawing function - should use the D3 selection, enter, exit
 * @param _options -- only needed if different kinds of updates are needed
 */
CloudVis.prototype.updateVis = function(){

    // TODO: implement update graphs (D3: update, enter, exit)


}

/**
 * Gets called by event handler and should create new aggregated data
 * aggregation is done by the function "aggregate(filter)". Filter has to
 * be defined here.
 * @param selection
 */
CloudVis.prototype.onSelectionChange= function (selectionStart, selectionEnd){

    // TODO: call wrangle function

    // do nothing -- no update when brushing

}

CloudVis.prototype.onPlateChange= function (d){


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

CloudVis.prototype.collide =  function(node) {
  var r = node.radius + 16,
      nx1 = node.x - r,
      nx2 = node.x + r,
      ny1 = node.y - r,
      ny2 = node.y + r;
  return function(quad, x1, y1, x2, y2) {
    if (quad.point && (quad.point !== node)) {
      var x = node.x - quad.point.x,
          y = node.y - quad.point.y,
          l = Math.sqrt(x * x + y * y),
          r = node.radius + quad.point.radius;
      if (l < r) {
        l = (l - r) / l * .5;
        node.x -= x *= l;
        node.y -= y *= l;
        quad.point.x += x;
        quad.point.y += y;
      }
    }
    return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
  };
}








