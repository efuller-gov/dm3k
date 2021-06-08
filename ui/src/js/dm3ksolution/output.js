function drawOutput(data){
    console.log("\n****** Draw solution visualization ******")
    // console.log(data)
    let ft = data["full_trace"]
    let res = ft["resource"]
    let act = ft["activity"]
    let table = []

    const reducer = (accumulator, currentValue) => accumulator + currentValue;
    /* TBD next:
    x add class type containers (blue and brown in mockup)
    - sort by instance width
    x add extra spacing between class type groups
    - transform input into hardcoded data structures
    - relative sizing and margin within the modal
    */

    // **************************************************************** //
    // HARDCODE. Would want to translate input to these data formats
    // **************************************************************** //
    // $("#widthFunctionToggle").change(
    //     function(){
    //         console.log("-----> width toggle changed")
    //         console.log(this)
    //         var item=$(this);
    //         console.log(item.val())
    //         //draw(widthFunc);
    //     }
    // )
    // NOTE: when you translate this from the input- maybe think about tying it in to the width resizing function. Width function determines the "value" field
    // as well as the col field. The rows are ordered as they come in- nothing to do there.

    //generateMatrix(widthFunc)
    let activity_dict = [
        {"name": "startup_Activity_instance_0", "class": "startup", "instance": 0, "instance_width": 0, "row": 0, "col": 0, "percentage": 0, "x": false, "cum_height": 0, "value": 1/(1.2+3)},
        {"name": "startup_Activity_instance_1", "class": "startup", "instance": 1, "instance_width": 0, "row": 0, "col": 1, "percentage": 0, "x": false, "cum_height": 0, "value": 1/(2.5+5)},
        {"name": "startup_Activity_instance_2", "class": "startup", "instance": 2, "instance_width": 0, "row": 0, "col": 2, "percentage": 0, "x": false, "cum_height": 0, "value": 2/(2.2+2)},
        {"name": "startup_Activity_instance_3", "class": "startup", "instance": 3, "instance_width": 0, "row": 0, "col": 3, "percentage": 0, "x": false, "cum_height": 0, "value": 1/(0.5+1)},
        {"name": "startup_Activity_instance_4", "class": "startup", "instance": 4, "instance_width": 0, "row": 0, "col": 4, "percentage": 0, "x": false, "cum_height": 0, "value": 2/(3.2+8)},
        {"name": "charity_Activity_instance_0", "class": "charity", "instance": 0, "instance_width": 0, "row": 1, "col": 5, "percentage": 0, "x": false, "cum_height": 0, "value": 1/5},
        {"name": "charity_Activity_instance_1", "class": "charity", "instance": 1, "instance_width": 0, "row": 1, "col": 6, "percentage": 0, "x": false, "cum_height": 0, "value": 1/2},
        {"name": "charity_Activity_instance_2", "class": "charity", "instance": 2, "instance_width": 0, "row": 1, "col": 7, "percentage": 0, "x": false, "cum_height": 0, "value": 2/3},
        {"name": "charity_Activity_instance_3", "class": "charity", "instance": 3, "instance_width": 0, "row": 1, "col": 8, "percentage": 0, "x": false, "cum_height": 0, "value": 1/1},
    ]
    let resource_dict = [
        {"name": "funding_Resource_instance_0", "class": "funding", 'instance_height': 0, "instance": 0, "budget": 3.2,  "row": 0, "cum_width": 0, "y": false, "data_col": 0},
        {"name": "funding_Resource_instance_1", "class": "funding", 'instance_height': 0, "instance": 1, "budget": 5.4,  "row": 1, "cum_width": 0, "y": false, "data_col": 0},
        {"name": "staff_Resource_instance_0",   "class": "staff",   'instance_height': 0, "instance": 0, "budget": 10,   "row": 2, "cum_width": 0, "y": false, "data_col": 1},
        {"name": "staff_Resource_instance_1",   "class": "staff",   'instance_height': 0, "instance": 1, "budget": 15,   "row": 3, "cum_width": 0, "y": false, "data_col": 1},
    ]
    // total_width values are the sum of the "value" in instance_cost_reward_dict
    let instances_per_activity_class = [
        {"class": "startup", "value": 5, "total_width": 0, "percentage": 0},
        {"class": "charity", "value": 4, "total_width": 0, "percentage": 0},
    ]
    let instances_per_resource_class = [
        {"class": "funding", "value": 2, "total_height": 0, "percentage": 0},
        {"class": "staff",   "value": 2, "total_height": 0, "percentage": 0},
    ]
    // **************************************************************** //
    // END HARDCODE.
    // **************************************************************** //
    
    // Plotting vars
    var x_pad=10, y_pad=10, class_y_pad = 0, class_x_pad=0, class_padding=25;
    var containerWidth = +d3.select('#soln-visualization').style('width').slice(0, -2)/1.5;
    var containerHeight = containerWidth/2;
    var classBoxSize = 40;
    var margin = {"left": 12, "top": containerWidth/25};
    var classLabelFontSize = "12px";
    var instanceLabelFontSize = "10px";
    
    // **************************************************************** //
    // Get percentages of class height for total container height,
    // and percentages of instances under class heights
    // **************************************************************** //
    // Looping over unique resource classes --> funding, staff
    for (let c of _.uniq(resource_dict.map(x=>x.class))){
        // compute s, sum of "value", or height for each class --> total height for each class type
        let s = resource_dict.filter(x=>x.class==c).map(x=>x.budget).reduce(reducer)
        instances_per_resource_class.filter(x=>x.class==c)[0].total_height = s;
    }
    // Get total height for all resource classes
    let total_height_all_classes = instances_per_resource_class.map(x=>x.total_height).reduce(reducer)
    // Compute percent of each instance of a class type's height
    for (let inst of instances_per_resource_class) {
        inst.percentage = inst.total_height/total_height_all_classes;
    }
    // Get percentage of instances for each class. Loop over every instance
    for (let inst of resource_dict) {
        inst.percentage = inst.budget/total_height_all_classes;
        let cur_class_name = inst.name.split("_")[0];
        let class_portion = instances_per_resource_class.filter(x=>x.class==cur_class_name)[0].percentage;
        let instance_portion = resource_dict.filter(x=>x.name==inst.name)[0].percentage;
        let h = containerHeight * class_portion * instance_portion;
        inst.instance_height = h;
    }
    // Compute total heights per class for class label boxes
    for (let inst of instances_per_resource_class){
        inst.total_height = resource_dict.filter(x=>x.class==inst.class).map(x=>x.instance_height).reduce(reducer)
    }

    // **************************************************************** //
    // Get percentages of class widths for total container width,
    // and percentages of instances under class widths
    // **************************************************************** //
    // Looping over unique activity classes --> startup, charity
    for (let c of _.uniq(activity_dict.map(x=>x.class))){
        // compute s, sum of "value", or width for each class --> total width for each class type
        let s = activity_dict.filter(x=>x.class==c).map(x=>x.value).reduce(reducer)
        instances_per_activity_class.filter(x=>x.class==c)[0].total_width = s;
    }
    // Get total width for all activity classes
    let total_width_all_classes = instances_per_activity_class.map(x=>x.total_width).reduce(reducer)
    // Compute percent of each instance of a class type's width
    for (let inst of instances_per_activity_class) {
        inst.percentage = inst.total_width/total_width_all_classes;
    }
    // Get percentage of instances for each class. Loop over every instance
    for (let inst of activity_dict) {
        inst.percentage = inst.value/total_width_all_classes;
        let cur_class_name = inst.name.split("_")[0];
        let class_portion = _.filter(instances_per_activity_class, function(x){return x.class == cur_class_name})[0]["percentage"];
        let instance_portion = _.filter(activity_dict, function(x){return x.name == inst.name})[0]["percentage"];
        // instances_per_activity_class.filter(x=>x.class==cur_class_name)[0].total_width = containerWidth * class_portion
        let w = containerWidth * class_portion * instance_portion;
        inst.instance_width = w;
    }
    // Compute total heights per class for class label boxes
    for (let inst of instances_per_activity_class){
        inst.total_width = activity_dict.filter(x=>x.class==inst.class).map(x=>x.instance_width).reduce(reducer)
    }

    // Sort by width function
    // activity_instances_width.sort((a, b) => parseFloat(b.w) - parseFloat(a.w));
    // activity_instances_width.sort((a, b) => parseFloat(a.row) - parseFloat(b.row));
    // console.log("WIDTHS ", activity_instances_width)

    // **************************************************************** //
    // Construct the matrix for plotting
    // **************************************************************** //
    for (let i = 0; i < res.length; i++) {
        let a = act[i];
        let r = res[i];
        let cur_act_inst = a.split("_").slice(-1)[0];
        let cur_res_inst = r.split("_").slice(-1)[0];

        let r_dict = resource_dict.filter(x=>(x.name==r))[0];
        let a_dict = activity_dict.filter(x=>(x.name==a))[0];

        let col_num = activity_dict.filter(x=>x.name==a)[0].col;
        let row_num = r_dict.row;

        let budget = ft.budget_used[i][r_dict.data_col];
        
        let w = a_dict.instance_width;
        let h = r_dict.instance_height;

        // Increment resource y value if its the first encounter
        if (cur_act_inst==0 && r_dict.y==false){
            r_dict.y = a_dict.cum_height;
        }
        // Increment activity x value if its the first encounter
        if (cur_res_inst==0 && a_dict.x==false){
            a_dict.x = r_dict.cum_width;
        }
        // Add extra padding between class types
        if (cur_res_inst==0){
            class_y_pad = class_padding;
        }
        if (cur_act_inst==0){
            class_x_pad = class_padding;
        }
        table.push({
            resource: r,
            activity: a,
            budget_used: budget,
            col: col_num,
            row: row_num,
            w: w,
            h: h,
            x: r_dict.cum_width + x_pad + class_x_pad,
            y: r_dict.y + y_pad + class_y_pad,
            fill_opacity: budget/r_dict.budget,
            total_resource_budget: r_dict.budget,
        })
        // Increment cumulative width for every activity instance
        r_dict.cum_width += (w+x_pad+class_x_pad);
        a_dict.cum_height += (h+y_pad+class_y_pad);
        class_y_pad = 0;
        class_x_pad = 0;
      }
    //end generateMatrix()

    // **************************************************************** //
    // D3 Plotting
    // **************************************************************** //
    // Empty div first
    //draw(table)
    d3.select('#soln-visualization').selectAll("*").remove();

    var grid = d3.select("#soln-visualization").append("svg")
        .style("width", "98%")
        .style("height", "600px")
        .attr("class", "grid")
        .append("g")
            .attr("transform",
              "translate(" + margin.left + "," + margin.top + ")");
    

    var div = d3.select("#soln-visualization").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);
    
    // **************************************************************** //
    // Resource Class Boxes
    // **************************************************************** //
    var resourceClassRect = grid.selectAll(".resourceClassRect")
        .data(instances_per_resource_class)
        .enter().append("g")
        .attr("transform", function(d, i) { return "translate(0,"+(classBoxSize*3)+")"; })

    resourceClassRect.append('rect')
        .attr("x", function (d) {
            return 0;
        })
        .attr("y", function (d) {
            return resource_dict.filter(x=>x.name==d.class+"_Resource_instance_0")[0].y + class_padding + y_pad;
        })
        .attr("width", classBoxSize)
        .attr("height", function (d) {
            return d.total_height + (d.value-1)*y_pad;
        })
        .style("fill", '#E9EDF1')
        .style("stroke", '#E9EDF1')
        .style('stroke-width', '1px')

    resourceClassRect.append("text")
        .style("font-size", classLabelFontSize)
        .attr("x", function (d) {
            // return -classBoxSize/2;
            return 0;
        })
        .attr("y", function (d) {
            // return resource_dict.filter(x=>x.name==d.class+"_Resource_instance_0")[0].y + class_padding + 2*y_pad + d.total_height/2;
            return resource_dict.filter(x=>x.name==d.class+"_Resource_instance_0")[0].y + class_padding;
        })
        .text(function(d) { return d.class; });

    // **************************************************************** //
    // Resource Instance Boxes
    // **************************************************************** //
    var resourceInstRect = grid.selectAll(".resourceInstRect")
        .data(resource_dict)
        .enter().append("g")
        .attr("transform", function(d, i) { return "translate(0,"+(classBoxSize*3)+")"; })

    resourceInstRect.append('rect')
        .attr("x", function (d) {
            return classBoxSize + x_pad;
        })
        .attr("y", function (d) {
            return table.filter(x=>((x.resource==d.name)&&(x.row==d.row)))[0].y;
        })
        .attr("width", classBoxSize)
        .attr("height", function (d) {
            return d.instance_height;
        })
        .style("fill", '#E9EDF1')
        .style("stroke", '#E9EDF1')
        .style('stroke-width', '1px')
    
    resourceInstRect.append("text")
        .style("font-size", instanceLabelFontSize)
        .attr("x", function (d) {
            return classBoxSize*2 + x_pad*1.5;
        })
        .attr("y", function (d) {
            return table.filter(x=>((x.resource==d.name)&&(x.row==d.row)))[0].y + y_pad;
        })
        .text(function(d) { return d.instance; });

    // **************************************************************** //
    // Activity Class Boxes
    // **************************************************************** //
    var activityClassRect = grid.selectAll(".activityClassRect")
        .data(instances_per_activity_class)
        .enter().append("g")
        .attr("transform", function(d, i) { return "translate("+(classBoxSize*4-x_pad/2)+", 0)"; })

    activityClassRect.append('rect')
        .attr("x", function (d, i) {
            return activity_dict.filter(x=>x.name==d.class+"_Activity_instance_0")[0].x;
        })
        .attr("y", function (d) {
            return 0;
        })
        .attr("width", function (d) {
            return d.total_width + (d.value-1)*x_pad;
        })
        .attr("height", classBoxSize)
        .style("fill", '#F1EFE9')
        .style("stroke", '#F1EFE9')
        .style('stroke-width', '1px')

    activityClassRect.append("text")
        .style("font-size", classLabelFontSize)
        .attr("x", function (d, i) {
            // return activity_dict.filter(x=>x.name==d.class+"_Activity_instance_0")[0].x + d.total_width/2;
            return activity_dict.filter(x=>x.name==d.class+"_Activity_instance_0")[0].x + x_pad;
        })
        .attr("y", function (d) {
            return classBoxSize/2;
        })
        .text(function(d) { return d.class; });

    // **************************************************************** //
    // Activity Instance Boxes
    // **************************************************************** //
    var activityInstRect = grid.selectAll(".activityInstRect")
        .data(activity_dict)
        .enter().append("g")
        .attr("transform", function(d, i) { return "translate("+(classBoxSize*4)+", 0)"; })

    activityInstRect.append('rect')
        .attr("x", function (d) {
            return table.filter(x=>((x.activity==d.name)&&(x.col==d.col)))[0].x - classBoxSize;
        })
        .attr("y", function (d) {
            return classBoxSize + y_pad; 
        })
        .attr("width", function (d) {
            return d.instance_width;
        })
        .attr("height", classBoxSize)
        .style("fill", '#F1EFE9')
        .style("stroke", '#F1EFE9')
        .style('stroke-width', '1px')

    activityInstRect.append("text")
        .style("font-size", instanceLabelFontSize)
        .attr("x", function (d) {
            return table.filter(x=>((x.activity==d.name)&&(x.col==d.col)))[0].x - classBoxSize;
        })
        .attr("y", function (d) {
            return classBoxSize*2 + y_pad*2.5;
        })
        .text(function(d) { return d.instance; });

    // **************************************************************** //    
    // Allocation (Resource * Activity) boxes to fill out matrix
    // **************************************************************** //
    grid.selectAll(".allocRect")
        .data(table)
        .enter().append('rect')
        .attr("transform", function(d, i) { return "translate("+(classBoxSize*3)+","+(classBoxSize*3)+")"; })
        .attr("x", function (d) {
            return d.x;
        })
        .attr("y", function (d) {
            return d.y;
        })
        .attr("width", function (d) {
            return d.w;
        })
        .attr("height", function (d) {
            return d.h;
        })
        .style("fill", '#9DB398')
        .style("stroke", '#9DB398')
        .style('stroke-width', '1px')
        .style("fill-opacity", function (d) {
            return d.fill_opacity;
        })
        .on('mouseover', function (d) {
            d3.select(this)
                .style('stroke', '#707070')
                .style('stroke-width', '2.5px')
                .style('border', '1px solid #707070')
            div.transition()
                .duration(200)
                .style("opacity", 1);
            div.html( "<b>"+
                        "Resource: </b>"+d.resource+ "<br/><b>" +
                        "Activity: </b>"+d.activity + "<br/><b>"+
                        "Budget used: </b>"+d.budget_used+" / "+d.total_resource_budget)
                .style("left", (d3.event.layerX) + "px")
                .style("top",  (d3.event.layerY*1.25) + "px");
        })
        .on('mouseout', function (d) {
            d3.select(this)
                .style('stroke', '#9DB398')
                .style('stroke-width', '1px')
                .style('border', '1px solid #9DB398')
            div.transition()
                .duration(500)
                .style("opacity", 0);
        })


    console.log("****** {END} Draw solution visualization ******\n")
}
