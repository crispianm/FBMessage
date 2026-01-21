function barChart(config_global) {
  var h_bar = 12,
      onMouseover = function(){}


  function chart(bc){
    bc.xScale.domain([0, d3.max(bc.nested_data, function(d) {return d.value;})])
  // Consistent inner padding around bars
  var topPad = 8;
  var bottomPad = 8;

    // On click, change the appearance of the bars, filter everything, and update barcharts, curves, and scatterplot
    function onClick(d){
      gtag('event', 'Histogram', {
           'event_category': 'Filter',
           'event_label': bc.title})

       // Update the "clicked" sets
       if (bc.clicked.has(d.key)) {
         bc.clicked.delete(d.key)
       } else {
         bc.clicked.add(d.key)
       }

       // Apply filters
       if (bc.clicked.size == 0) {
         bc.dimension.filter()
       } else {
          bc.dimension.filter(function(a){return bc.clicked.has(a)})
       }

       // Update to match new filters
       update_all()
    }

    // On mouseover, display tooltip
    function onMouseover(d){
      div.transition()
         .duration(200)
         .style("opacity", .9);
      div.html(bc.get_tooltip(d.key))
         .style("left", (d3.event.pageX) + "px")
         .style("top", (d3.event.pageY - 28) + "px");
      d3.select(this).classed("mouseovered", true);
    }

    // On mouseout, hide the tooltip
    function onMouseout(d){
      div.transition()
         .duration(200)
         .style("opacity", 0);
      d3.select(this).classed("mouseovered", false);
    }

    // Calculate available width from the container at render time
    var containerW = 0;
    try {
      containerW = Math.max(0, bc.div_body.node().getBoundingClientRect().width - (margin3.left + margin3.right));
    } catch(e) {
      containerW = (typeof w3 !== 'undefined' ? w3 : 300);
    }
    // Sync the scale range to the real container width
    if (bc.xScale && containerW > 0) {
      bc.xScale.range([0, containerW]);
    }

    // Select the svg element, if it exists.
    var svg = bc.div_body.selectAll("svg").data([bc.nested_data]);

    // Otherwise, create the skeletal chart.
    var svgEnter = svg.enter().append("svg");

    // Create a group for each bar. We will then add the bar and the labels to these groups
  var bar_elements = svgEnter.selectAll(".bar-element")
        .data(bc.nested_data).enter()
        .append("g")
        .attr("class", "bar-element")
        // .attr("id", function(d){try {return this_temp.get_data(d)} catch {return "other"}})
    .attr("transform", function(d, i) { return "translate(" + margin3.left + "," + (topPad + i*(h_bar+2)) + ")"; });

    bc.xScale.domain([0, d3.max(bc.nested_data, function(d) {return d.value;})])

    // Add bars
  var leftLabelPad = 0; // bars start at x=0 because group already accounts for left margin
  bar_elements.append("rect")
        .attr("class", "bar")
        .attr("height", h_bar)
        .attr("width", function(d) {
          var w = bc.xScale(d.value);
          var maxW = (bc.xScale.range ? bc.xScale.range()[1] : w);
          return Math.max(0, Math.min(w, maxW));
        })
    // x=0 is already offset by the group's left translate
        .style("fill", function(d){if(bc.isColoredBarchart){return colorScale(d.key)} else {return ""}})
        .classed("unclicked", function(d){return !(bc.clicked.size == 0 || bc.clicked.has(d.key))})
        .on("click", onClick)
        .on("mouseover", onMouseover)
        .on("mouseout", onMouseout)

    // Add number-labels to bar charts (place inside the bar to avoid cropping)
    bar_elements.append("text")
      .attr("class", "legend_hist_num")
      .attr("dy", "0.35em")
      .attr("y", h_bar/2 + "px")
      .attr("x", function(d) {
        var w = bc.xScale(d.value);
        var maxW = (bc.xScale.range ? bc.xScale.range()[1] : w);
        var end = Math.max(0, Math.min(w, maxW));
        // Keep label within the bar area; if too small, place at a minimum x
        return end >= 20 ? end - 4 : Math.max(12, end + 2);
      })
      .attr("text-anchor", function(d){
        var w = bc.xScale(d.value);
        var maxW = (bc.xScale.range ? bc.xScale.range()[1] : w);
        return Math.min(w, maxW) >= 20 ? "end" : "start";
      })
      .text(function(d) { return d.value; })
      .on("click", onClick)
      .on("mouseover", onMouseover)
      .on("mouseout", onMouseout)

    // Add labels to bar charts
  bar_elements.append("text")
        .attr("class", "legend_hist_text")
        .attr("dy", "0.35em")
        .attr("y", h_bar/2 + "px")
    .attr("x", -8)
    .attr("text-anchor", "end")
        .text(function(d){return bc.get_legend(d.key)})
        .on("click", onClick)
        .on("mouseover", onMouseover)
        .on("mouseout", onMouseout)

    // Adjust svg size explicitly based on container width and number of bars
    // This prevents horizontal cropping when the sidebar is narrow
  var barsCount = bc.nested_data ? bc.nested_data.length : 0;
  var svgWidth = (margin3.left + (bc.xScale.range ? bc.xScale.range()[1] : 0) + margin3.right);
  var svgHeight = (topPad + barsCount * (h_bar + 2) + bottomPad);
    // Fallbacks if ranges are not ready
  if (!svgWidth || svgWidth <= 0) { svgWidth = (margin3.left + (typeof w3 !== 'undefined' ? w3 : 300) + margin3.right); }
  if (!svgHeight || svgHeight <= 0) { svgHeight = (topPad + 10 * (h_bar + 2) + bottomPad); }

    svgEnter
      .style("width", "100%")
      .attr("height", svgHeight + "px")
      .attr("viewBox", "0 0 " + svgWidth + " " + svgHeight)
      .attr("preserveAspectRatio", "xMinYMin meet");

    // Also update existing SVGs if re-rendering
    svg
      .attr("height", svgHeight + "px")
      .attr("viewBox", "0 0 " + svgWidth + " " + svgHeight)
      .attr("preserveAspectRatio", "xMinYMin meet")
      .style("width", "100%");
  }
  return chart
}
