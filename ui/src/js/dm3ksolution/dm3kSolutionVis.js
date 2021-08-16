import $ from 'jquery'
import lodash from 'lodash'
import * as d3 from 'd3'

export class Dm3kSolutionVis{
    constructor() {
        // this.reducer = (accumulator, currentValue) => accumulator + currentValue;
    }

    generateSolnMatrix(solnMatrixObj){
        let data = solnMatrixObj.data
        let outline = solnMatrixObj.problemData
        let widthFunc = solnMatrixObj.width
        // Plotting vars
        let x_pad=10, y_pad=10, class_y_pad = 0, class_x_pad=0, class_padding=25;
        let svgContainerWidth = +d3.select('#soln-visualization').style('width').slice(0, -2)/1.5;

        let ft = data["full_trace"]
        let res = ft["resource"]
        let act = ft["activity"]
        let budget_used = ft["budget_used"]
        let selected = ft["selected"]
        let table = []
        let resource_dict = []
        let activity_dict = []
        let instances_per_resource_class = []
        let instances_per_activity_class = []
        let resource_name_label_map = []
        let activity_name_label_map = []
        let res_containers = []
        let act_containers = []
        let budget_dict = []
        let selected_dict = []
        let classBoxSize = 30;

        const reducer = (accumulator, currentValue) => accumulator + currentValue;
        // console.log("**********************************************")
        // console.log("Problem outline ", outline)
        // console.log("Backend output ", data)
        // console.log("**********************************************")

        let act_list = lodash.uniq(act)

        // Populate budget dict for when I rearrange act and res lists
        for (let i = 0; i < res.length; i++) {
            budget_dict.push({
                r: res[i],
                a: act[i],
                b: budget_used[i]
            })
        }
        for (let i = 0; i < res.length; i++) {
            selected_dict.push({
                r: res[i],
                a: act[i],
                s: selected[i]
            })
        }

        // **************************************************************** //
        // Add classLabels to outline.<a/r>Instances and outline.<a/r>Classes
        // **************************************************************** //
        for (let ri of outline.resourceInstances){
            let rc = outline.resourceClasses.filter(x=>x.className==ri.className)[0]
            let inst_class_name = rc.className.toLowerCase();
            ri.classLabel = inst_class_name;
            rc.classLabel = inst_class_name;
            // containers whose parents match rc
            let container_parent_match = outline.containsInstances.filter(x=>x.parentClassName==rc.className)[0]
            if (container_parent_match != undefined){
                // This needs to be for EACH
                container_parent_match.parentClassLabel = inst_class_name
            }
            // containers whose children match rc
            let container_child_match = outline.containsInstances.filter(x=>x.childClassName==rc.className)[0]
            if (container_child_match != undefined){
                container_child_match.childClassLabel = inst_class_name
            }
        }
        // Add classLabel to activityInstances and activityClasses, sourced from the activityClass
        for (let ai of outline.activityInstances){
            let ac = outline.activityClasses.filter(x=>x.className==ai.className)[0]
            let inst_class_name = ac.className.toLowerCase();
            ai.classLabel = inst_class_name;
            ac.classLabel = inst_class_name;
            // containers whose parents match rc
            let container_parent_match = outline.containsInstances.filter(x=>x.parentClassName==ac.className)[0]
            if (container_parent_match != undefined){
                // This needs to be for EACH
                container_parent_match.parentClassLabel = inst_class_name
            }
            // containers whose children match rc
            let container_child_match = outline.containsInstances.filter(x=>x.childClassName==ac.className)[0]
            if (container_child_match != undefined){
                container_child_match.childClassLabel = inst_class_name
            }
        }

        // **************************************************************** //
        // Populate resource_dict
        // **************************************************************** //
        let inst_index=0, class_index=0;
        let last_class = lodash.uniq(res)[0].split("_")[0];
        // Need to add tag to instances in outline so I can grab them regardless of what user names then
        // instanceLabel = <className>_Resource_instance_<index>
        // Loop through all resource instances. Create unique labels for them.
        // If the resource's class object in resourceClasses identifies it as a container, add it to the container list.
        let ind = 0;
        for (let r of outline.resourceInstances){
            ind = 0;
            let res_class_entry = outline.resourceClasses.filter(x=>x.classLabel == r.classLabel)[0];
            if (res_class_entry.containsClasses.length > 0){
                res_containers = res_containers.concat(outline.containsInstances.filter(x=>x.parentClassName==res_class_entry.className))
            }
            for (let ri of r.instanceTable){
                // within outline, set instance label to lower case class name --> class name from resourceInstances
                ri.instanceLabel = r.className.toLowerCase()+"_"+"Resource_instance_"+ind;
                
                resource_name_label_map.push({
                    label: ri.instanceLabel,
                    name: ri.instanceName,
                    original_name: ri.instanceName
                })
                ind++;
            }
        }
        // Overwrite res list with labels
        for (let i = 0; i < res.length; i++) {
            res[i] = resource_name_label_map.filter(x=> (x.name==res[i]) || (x.label==res[i]) )[0].label
        }
        // Now loop through unique resource labels, and populate resource dict with each resource instance's info
        for (let r of lodash.uniq(res)) {
            let cur_class = r.split("_")[0].toLowerCase();
            if (last_class!=cur_class){
                class_index++;
            }
            let budget_obj = outline.resourceInstances.filter(x=>x.className.toLowerCase()==cur_class)[0].instanceTable.filter(x=>x.instanceLabel==r)[0].budget;
            let budget_unit = Object.keys(budget_obj)[0];
            resource_dict.push({
                name: r,
                original_name: resource_name_label_map.filter(x=>x.label==r)[0].original_name,
                class: r.split("_")[0],
                instance: r.split("_").slice(-1)[0],
                budget: budget_obj[budget_unit],
                budget_unit: budget_unit,
                row: inst_index,
                data_col: class_index,
                instance_height: 0,
                cum_width: 0,
                y: false,
            })
            inst_index++;
            last_class=cur_class;
        }

        // **************************************************************** //
        // Populate activity_dict
        // **************************************************************** //
        let reward=0, cost=0, width_value=0;
        inst_index=0, class_index=0;

        // Loop through all activity instances and give them a unique label.
        // If class object identifies them as a container, add them to the container list.
        for (let a of outline.activityInstances){
            ind = 0;
            let act_class_entry = outline.activityClasses.filter(x=>x.classLabel == a.classLabel)[0];
            if (act_class_entry.containsClasses.length > 0){
                act_containers.push(outline.containsInstances.filter(x=>x.parentClassName==act_class_entry.className)[0])
            }
            for (let i of a.instanceTable){
                i.instanceLabel = a.className.toLowerCase()+"_"+"Activity_instance_"+ind;
                
                activity_name_label_map.push({
                    label: i.instanceLabel,
                    name: i.instanceName,
                    original_name: i.instanceName
                })
                ind++;
            }
        }

        // Overwrite act list with unique labels
        for (let i = 0; i < act_list.length; i++) {
            act_list[i] = activity_name_label_map.filter(x=> (x.name==act_list[i]) || (x.label==act_list[i]) )[0].label
        }

        // **************************************************************** //
        // 1) Inherit rewards from container instances
        // 2) Create sorting indices for cost, reward, ratio
        // **************************************************************** //
        for (let j=0; j<outline.activityInstances.length; j++){
            let u_activity_instance = outline.activityInstances[j];
            let instance_table = u_activity_instance.instanceTable;
            for (let i=0; i<instance_table.length; i++){
                let cur_act_inst = instance_table[i]
                // calculate aggregate cost
                let ck = Object.keys(cur_act_inst.cost)
                let agg_cost = 0
                for (let ii=0; ii<ck.length; ii++){
                    agg_cost = agg_cost+cur_act_inst.cost[ck[ii]]
                }
                instance_table[i].agg_cost = agg_cost;
                // calculate aggregate reward over containers
                let cur_class = instance_table[i].instanceName.split("_")[0].toLowerCase();            
                let agg_reward = this.inheritContainerRewards(
                    cur_class, 
                    cur_act_inst.instanceName,
                    act_containers,
                    outline.activityInstances,
                    cur_act_inst.reward
                )
                instance_table[i].agg_reward = agg_reward;
                // calculate r/c ratio
                instance_table[i].ratio = agg_reward/agg_cost;
                if (agg_reward == 0){
                    instance_table[i].ratio = 0.5
                }
                
            }

            let it_copy_sort_cost = instance_table.slice();
            it_copy_sort_cost.sort((b, a) => parseFloat(a.agg_cost) - parseFloat(b.agg_cost));

            // sort by reward
            let it_copy_sort_reward = instance_table.slice();
            it_copy_sort_reward.sort((b, a) => parseFloat(a.agg_reward) - parseFloat(b.agg_reward));
            
            // sort by ratio
            let it_copy_sort_ratio = instance_table.slice();
            it_copy_sort_ratio.sort((b, a) => parseFloat(a.ratio) - parseFloat(b.ratio));
            
            //default is sort by cost
            instance_table.sort((b, a) => parseFloat(a.agg_cost) - parseFloat(b.agg_cost));

            //assign sorted indices to instance objects
            for (let i=0; i<it_copy_sort_cost.length; i++){
                let tmp_ind = instance_table.findIndex(x=>x.instanceName==it_copy_sort_cost[i].instanceName)
                instance_table[tmp_ind].cost_desc_index = i;
                instance_table[tmp_ind].first_flag_cost = (i == 0) ? true : false;
            }
            for (let i=0; i<it_copy_sort_reward.length; i++){
                let tmp_ind = instance_table.findIndex(x=>x.instanceName==it_copy_sort_reward[i].instanceName)
                instance_table[tmp_ind].reward_desc_index = i;
                instance_table[tmp_ind].first_flag_reward = (i == 0) ? true : false;
            }
            for (let i=0; i<it_copy_sort_ratio.length; i++){
                let tmp_ind = instance_table.findIndex(x=>x.instanceName==it_copy_sort_ratio[i].instanceName)
                instance_table[tmp_ind].ratio_desc_index = i;
                instance_table[tmp_ind].first_flag_ratio = (i == 0) ? true : false;
            }
        }

        // Loop through unique activity instances and populate activity_dict with their width information, etc.
        // This is where activity_dict actually gets assigned
        last_class = act_list[0].split("_")[0];
        for (let a of act_list) {
            reward = 0;
            let cur_class = a.split("_")[0].toLowerCase();
            let cur_act_inst = outline.activityInstances.filter(x=>x.classLabel==cur_class)[0].instanceTable.filter(x=>x.instanceLabel==a)[0];
            
            reward = cur_act_inst.agg_reward;
            let cost_unit = Object.keys(cur_act_inst.cost);

            // class_index determines which col to place the rect in
            if (last_class!=cur_class){
                class_index = class_index+1;
            }

            // Get instance's reward and cost
            if (Array.isArray(cur_act_inst.cost)){
                cost = cur_act_inst.cost.reduce(reducer)
            } else {
                let ck = Object.keys(cur_act_inst.cost)
                cost = 0
                for (let i=0; i<ck.length; i++){
                    cost = cost+cur_act_inst.cost[ck[i]]
                }
                cost_unit = Object.keys(cur_act_inst.cost);
            }
            // Get selected or not
            let select_sum = selected_dict.filter(x=>x.a==activity_name_label_map.filter(x=>x.label==a)[0].original_name).map(x=>x.s).reduce(reducer);
            let selected_flag = (select_sum>0) ? 1 : 0;

            // Assign width value according to width function
            switch (widthFunc) {
                case "ratio":
                    width_value = reward/cost;
                    if (reward == 0){
                        width_value = 0.5
                    }
                    break;
                case "reward":
                    width_value = reward;
                    if (reward == 0){
                        width_value = 0.5 // TODO: Is there a better workaround than this to convey no reward?
                    }
                    break;
                case "cost":
                    width_value = cost;
                    break;
                default:
                    width_value = 0;
            }
            activity_dict.push({
                name: a,
                class: a.split("_")[0],
                instance: a.split("_").slice(-1)[0],
                value: width_value,
                col: class_index,
                instance_width: width_value,
                cum_height: 0,
                x: false,
                percentage: 0,
                reward: reward,
                cost: cost,
                cost_unit: cost_unit,
                original_name: activity_name_label_map.filter(x=>x.label==a)[0].original_name,
                ratio: reward/cost,
                cost_desc_index: cur_act_inst.cost_desc_index,
                reward_desc_index: cur_act_inst.reward_desc_index,
                ratio_desc_index: cur_act_inst.ratio_desc_index,
                first_flag_ratio : cur_act_inst.first_flag_ratio,
                first_flag_cost : cur_act_inst.first_flag_cost,
                first_flag_reward : cur_act_inst.first_flag_reward,
                selected: selected_flag        
            })
            inst_index++;
            last_class=cur_class;
        }
        
        // **************************************************************** //
        // Get percentages of class height for total container height,
        // and percentages of instances under class heights
        // **************************************************************** //
        // Looping over unique resource classes
        for (let c of lodash.uniq(resource_dict.map(x=>x.class))){
            // compute s, sum of "value", or height for each class --> total height for each class type
            let s = resource_dict.filter(x=>x.class==c).map(x=>x.budget).reduce(reducer)
            let budget_unit = resource_dict.filter(x=>x.class==c)[0].budget_unit
            instances_per_resource_class.push({
                class: c,
                value: resource_dict.filter(x=>x.class==c).length, //number of instances of this class
                total_height: s,
                total_budget: s,
                budget_unit: budget_unit,
                percentage: 0,
            })
        }

        // Get total height for all resource classes
        let total_height_all_classes = instances_per_resource_class.map(x=>x.total_height).reduce(reducer)
        // Compute percent of each instance of a class type's height
        for (let inst of instances_per_resource_class) {
            inst.percentage = inst.total_height/total_height_all_classes;
        }

        // Assign container dims
        // console.log("Can I access that const here? ", x_pad_dict)
        // x_pad = get_pad(activity_dict)
        // y_pad = get_pad(resource_dict)
        x_pad = lodash.max([this.get_pad(activity_dict), this.get_pad(resource_dict)])
        y_pad = lodash.max([this.get_pad(activity_dict), this.get_pad(resource_dict)])
        class_padding = this.get_class_pad(x_pad)
        classBoxSize = this.get_class_box_size(x_pad)
        // x_pad = (activity_dict.length>25) ? 5 : 10;
        // y_pad = (resource_dict.length>25) ? 5 : 10;

        let containerWidth = svgContainerWidth - res_containers.length*classBoxSize - classBoxSize*2 - activity_dict.length*x_pad - 
            (instances_per_activity_class.length)*class_padding;
        let containerHeight = containerWidth/1.5 -  act_containers.length*classBoxSize*2 - (instances_per_resource_class.length-1)*class_padding
        // -  act_containers.length*classBoxSize - (resource_dict.length-1)*x_pad - 
            // (instances_per_resource_class.length-1)*class_padding;

        // Get percentage of instances for each class. Loop over every instance
        for (let inst of resource_dict) {
            inst.percentage = inst.budget/total_height_all_classes;
            // let cur_class_name = inst.name.split("_")[0].toLowerCase();
            // let class_portion = instances_per_resource_class.filter(x=>x.class.toLowerCase()==cur_class_name)[0].percentage;
            let instance_portion = resource_dict.filter(x=>x.name==inst.name)[0].percentage;
            // let h = containerHeight * class_portion * instance_portion;
            let h = containerHeight * instance_portion;
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
        // Populate instances_per_activity_class. Looping over unique activity classes
        for (let c of lodash.uniq(activity_dict.map(x=>x.class))){
            let s = activity_dict.filter(x=>x.class==c).map(x=>x.value).reduce(reducer)
            instances_per_activity_class.push({
                class: c,
                value: activity_dict.filter(x=>x.class==c).length, //number of instances of this class
                total_width: s,
                percentage: 0,
            })

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
            // let cur_class_name = inst.name.split("_")[0].toLowerCase();
            // let class_portion = lodash.filter(instances_per_activity_class, function(x){return x.class.toLowerCase() == cur_class_name})[0]["percentage"];
            let instance_portion = lodash.filter(activity_dict, function(x){return x.name == inst.name})[0]["percentage"];
            // let w = containerWidth * class_portion * instance_portion;
            let w = containerWidth * instance_portion;
            inst.instance_width = w;
        }
        // Compute total widths per class for class label boxes
        for (let inst of instances_per_activity_class){
            inst.total_width = activity_dict.filter(x=>x.class==inst.class).map(x=>x.instance_width).reduce(reducer)
        }

        // **************************************************************** //
        // Add width and height info to containers based on how many
        // instances they contain
        // **************************************************************** //
        // TODO: why do containers of containers not show up?
        // maybe because they have no allocations associated?
        for (let rc of res_containers){
            let ri = resource_dict.filter(x=>x.class==rc.childClassLabel)
            if (rc.instanceTable[0].parentInstanceName=="ALL" & rc.instanceTable[0].childInstanceName=="ALL"){
                rc.total_height = ri.map(x=>x.instance_height).reduce(reducer)
                rc.num_contained_instances = ri.length
            } else {
                rc.total_height = ri.map(x=>x.instance_height).reduce(reducer) * (lodash.uniq(rc.instanceTable.map(x=>x.childInstanceName)).length/ri.length)
                rc.num_contained_instances = lodash.uniq(rc.instanceTable.map(x=>x.childInstanceName)).length
            }
            rc.row = lodash.min(ri.map(x=>x.row))
            rc.y = lodash.min(ri.map(x=>x.y))
            rc.num_instances = ri.length
        }
        for (let ac of act_containers){
            let ai = activity_dict.filter(x=>x.class==ac.childClassLabel)
            if (ai.length > 0){
                ai = activity_dict.filter(x=>x.class==ac.childClassLabel)
                if (ac.instanceTable[0].parentInstanceName=="ALL" & ac.instanceTable[0].childInstanceName=="ALL"){
                    ac.total_width = ai.map(x=>x.instance_width).reduce(reducer)
                    ac.num_contained_instances = ai.length
                } else {
                    ac.total_width = ai.map(x=>x.instance_width).reduce(reducer) * (lodash.uniq(ac.instanceTable.map(x=>x.childInstanceName)).length/ai.length)
                    ac.num_contained_instances = lodash.uniq(ac.instanceTable.map(x=>x.childInstanceName)).length
                }
                ac.num_instances = ai.length
            } else{
                ai = act_containers.filter(x=>x.childClassLabel==ac.childClassLabel)[0].instanceTable
                if (ac.instanceTable[0].parentInstanceName=="ALL" & ac.instanceTable[0].childInstanceName=="ALL"){
                    ac.total_width = ai.map(x=>x.instance_width).reduce(reducer)
                    ac.num_contained_instances = ai.length
                } else {
                    ac.total_width = ai.map(x=>x.instance_width).reduce(reducer) * (lodash.uniq(ac.instanceTable.map(x=>x.childInstanceName)).length/ai.length)
                    ac.num_contained_instances = lodash.uniq(ac.instanceTable.map(x=>x.childInstanceName)).length
                }
                ac.num_instances = ai.length
            }
        }

        // **************************************************************** //
        // Reconstruct res and act lists with all combinations
        // **************************************************************** //
        let new_res = []
        let new_act = []
        let new_budget_used = []
        let nd = [];

        let groupByClass = this.groupBy("class");
        let gpc = groupByClass(activity_dict);

        switch (widthFunc) {
            case "ratio":
                    for (let c of Object.keys(gpc)){
                        gpc[c].sort((a, b) => parseFloat(a.ratio_desc_index) - parseFloat(b.ratio_desc_index));
                        nd = nd.concat(gpc[c])
                    }
                    activity_dict = nd;
                break;
            case "reward":
                for (let c of Object.keys(gpc)){
                    gpc[c].sort((a, b) => parseFloat(a.reward_desc_index) - parseFloat(b.reward_desc_index));
                    nd = nd.concat(gpc[c])
                }
                activity_dict = nd;
                break;
            case "cost":
                for (let c of Object.keys(gpc)){
                    gpc[c].sort((a, b) => parseFloat(a.cost_desc_index) - parseFloat(b.cost_desc_index));
                    nd = nd.concat(gpc[c])
                }
                activity_dict = nd;
                break;
            default:
                break;
        }
        for (let i = 0; i < resource_dict.length; i++) {
            let ri = resource_dict[i]
            for (let j = 0; j < activity_dict.length; j++) {
                let aj = activity_dict[j]
                new_res.push(ri.name)
                new_act.push(aj.name)
                let cur_budget = budget_dict.filter(x=>( (x.a==aj.original_name || x.a==aj.name) && (x.r==ri.original_name || x.r==ri.name) ))
                if (cur_budget[0]!=undefined){
                    new_budget_used.push(cur_budget[0].b)
                } else {
                    let budget_len = outline.activityClasses.length
                    new_budget_used.push( new Array(budget_len).fill(0))
                }
            }
        }

        res = new_res
        act = new_act
        budget_used = new_budget_used

        // **************************************************************** //
        // Construct the matrix for plotting
        // **************************************************************** //

        // let last_res_class = res[0].split("_")[0].toLowerCase();
        let last_act_class = act[0].split("_")[0].toLowerCase();

        for (let i = 0; i < res.length; i++) {
            let a = act[i];
            let r = res[i];

            let cur_res_inst = r.split("_").slice(-1)[0];
            let cur_act_class = r.split("_")[0].toLowerCase();

            let r_dict = resource_dict.filter(x=>(x.name==r))[0];
            let a_dict = activity_dict.filter(x=>(x.name==a))[0];

            let col_num = activity_dict.filter(x=>x.name==a)[0].col;
            let row_num = r_dict.row;

            let budget = budget_used[i][r_dict.data_col];
            
            let w = a_dict.instance_width;
            let h = r_dict.instance_height;

            // Increment resource y value if its the first encounter
            if (cur_act_class!=last_act_class && r_dict.y==false){
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
            if ( (widthFunc=="ratio" && a_dict.first_flag_ratio) || 
                (widthFunc=="cost" && a_dict.first_flag_cost) || 
                (widthFunc=="reward" && a_dict.first_flag_reward) ){
                class_x_pad = class_padding;
            }

            table.push({
                resource: r,
                activity: a,
                resource_class: r.split('_')[0],
                activity_class: a.split('_')[0],
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
            // let cur_res_class = last_res_class;
            cur_act_class = last_act_class;
        }

        // console.log("resource_dict ", resource_dict)
        // console.log("instances_per_resource_class ", instances_per_resource_class)
        // console.log("res_containers ", res_containers)
        // console.log("activity_dict ", activity_dict)
        // console.log("instances_per_activity_class ", instances_per_activity_class)
        // console.log("act_containers ", act_containers)
        // console.log("table ", table)

        this.drawSolnOutput(
            table, 
            instances_per_resource_class,
            resource_dict,
            instances_per_activity_class,
            activity_dict,
            resource_name_label_map,
            activity_name_label_map,
            res_containers,
            act_containers,
            outline,
            widthFunc,
        )

    }

    drawSolnOutput(
                table, 
                instances_per_resource_class,
                resource_dict,
                instances_per_activity_class,
                activity_dict,
                resource_name_label_map,
                activity_name_label_map,
                res_containers,
                act_containers,
                outline,
                widthFunc
    ){
        // Plotting vars
        let x_pad=10, y_pad=10, class_padding=25;
        x_pad = lodash.max([this.get_pad(activity_dict), this.get_pad(resource_dict)])
        y_pad = lodash.max([this.get_pad(activity_dict), this.get_pad(resource_dict)])
        class_padding = this.get_class_pad(x_pad)
        let classBoxSize = this.get_class_box_size(x_pad)

        let containerWidth = +d3.select('#soln-visualization').style('width').slice(0, -2)/1.5;
        let margin = {"left": 0, "top": containerWidth/50};

        let classLabelFontSize = "0.55vw";
        let instanceLabelFontSize = "0.55vw";
        let containerLabelFontSize = "0.55vw";
        if (activity_dict.length > 15){
            classLabelFontSize = "0.4vw";
            instanceLabelFontSize = "0.3vw";
            containerLabelFontSize = "0.4vw";
        }
        let classLabelFontStyle = "normal";

        let res_hover_color = "#caced1";
        let res_base_color = "#E9EDF1";
        let act_base_color = '#F1EFE9';
        let act_hover_color = '#D9D7D2';
        let container_opacity = 0.3;
        
        let alloc_rect_stroke = "0.3px"

        // **************************************************************** //
        // D3 Plotting
        // **************************************************************** //
        // Empty div first
        d3.select('#soln-visualization').selectAll("*").remove();
        d3.select('#soln-explainer').selectAll("*").remove();

        function truncateDecimals(number, digits) {
            var multiplier = Math.pow(10, digits),
                adjustedNum = number * multiplier,
                truncatedNum = Math[adjustedNum < 0 ? 'ceil' : 'floor'](adjustedNum);
    
            return truncatedNum / multiplier;
        }
        const reducer = (accumulator, currentValue) => accumulator + currentValue;

        let grid = d3.select("#soln-visualization").append("svg")
            .attr("viewBox", `0 0 980 680`) //min-x, min-y, width, height
            // .attr("width", +d3.select('#soln-visualization').style('width').slice(0, -2))
            // .attr("height", (+d3.select('#soln-visualization').style('width').slice(0, -2))/1.5)
            .attr("class", "grid")
            .append("g")
                .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");
        
        let summary = d3.select("#soln-explainer").append("svg")
            .attr("viewBox", `0 0 500 500`)
            .attr("class", "summary")
            .append("g")
                .attr("transform",
                "translate(" + 0 + "," + 150 + ")");

        let div = d3.select("#soln-visualization").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);

        let x_ax_pos = classBoxSize*1.5;
        // let y_ax_pos = classBoxSize*1.5;
        let x_ax_pad = classBoxSize*2;
        // let y_ax_pad = classBoxSize;
        let y_ax_pad = 0;
        let dumbell_width = 10;

        // **************************************************************** //
        // Axes and labels
        // **************************************************************** //
        let resourceAx = grid.selectAll(".resourceAx")
            .data(instances_per_resource_class)
                .enter().append("g")
                .attr("transform", function() {
                    let xt = 0;
                    let yt = classBoxSize*3 + y_ax_pad;
                    if (act_containers.length > 0){
                        yt = act_containers.length*classBoxSize + classBoxSize*3 + y_ax_pad;
                    }
                    return "translate("+(xt)+","+(yt)+")"; 
                })

        resourceAx.append("line")
            .style("stroke", "#707070")
            .style('stroke-width', '1px')
            .attr("x1", x_ax_pos)
            .attr("y1", function (d) {
                return resource_dict.filter(x=>x.name==d.class+"_Resource_instance_0")[0].y + class_padding + y_pad;
            })
            .attr("x2", x_ax_pos)
            .attr("y2", function (d) {
                return resource_dict.filter(x=>x.name==d.class+"_Resource_instance_0")[0].y + 
                class_padding + y_pad + d.total_height + (d.value-1)*y_pad;
            })
        
        //top horizontal endline
        resourceAx.append("line")
            .style("stroke", "#707070")
            .style('stroke-width', '1px')
            .attr("x1", x_ax_pos-dumbell_width/2)
            .attr("y1", function (d) {
                return resource_dict.filter(x=>x.name==d.class+"_Resource_instance_0")[0].y + class_padding + y_pad;
            })
            .attr("x2", x_ax_pos+dumbell_width/2) 
            .attr("y2", function (d) {
                return resource_dict.filter(x=>x.name==d.class+"_Resource_instance_0")[0].y + class_padding + y_pad;
            })

        //bottom horizontal endline
        resourceAx.append("line")
            .style("stroke", "#707070")
            .style('stroke-width', '1px')
            .attr("x1", x_ax_pos-dumbell_width/2)
            .attr("y1", function (d) {
                return resource_dict.filter(x=>x.name==d.class+"_Resource_instance_0")[0].y + 
                class_padding + y_pad + d.total_height + (d.value-1)*y_pad;
            })
            .attr("x2", x_ax_pos+dumbell_width/2) 
            .attr("y2", function (d) {
                return resource_dict.filter(x=>x.name==d.class+"_Resource_instance_0")[0].y + 
                class_padding + y_pad + d.total_height + (d.value-1)*y_pad;
            })

        
        resourceAx.append("text")
            .style("font-size", containerLabelFontSize)
            .style("fill", "#707070")
            .attr("x", 0)
            .attr("y", function (d) {
                return lodash.min(resource_dict.filter(x=>x.class==d.class).map(x=>x.y)) + class_padding + y_pad + 
                (d.total_height + (d.value-1)*y_pad)/2
            })
            .attr("dy", "0em")
            .text(function(d) {
                return truncateDecimals(d.total_budget, 1);

            })

        resourceAx.append("text")
            .style("font-size", containerLabelFontSize)
            .style("fill", "#707070")
            .attr("x", 0)
            .attr("y", function (d) {
                return lodash.min(resource_dict.filter(x=>x.class==d.class).map(x=>x.y)) + class_padding + y_pad + 
                (d.total_height + (d.value-1)*y_pad)/2
            })
            .attr("dy", "1em")
            .text(function(d) {
                return d.budget_unit;

            })
        
        let activityAx = grid.selectAll(".activityAx")
            .data(instances_per_activity_class)
                .enter().append("g")
                .attr("transform", function() {
                    let xt = classBoxSize*3 + x_ax_pad;
                    let yt = lodash.max(table.map(x=>x.y)) + table.filter(x=>x.y==lodash.max(table.map(x=>x.y)))[0].h + 
                        classBoxSize*4 + classBoxSize/2;
                    if (res_containers.length > 0){
                        xt = classBoxSize*4 + x_ax_pad;
                    }
                    if (act_containers.length > 0){
                        yt = yt + (act_containers.length+1)*(classBoxSize/2);
                    }
                    return "translate("+(xt)+","+(yt)+")"; 
                })    

        activityAx.append("line")
            .style("stroke", "#707070")
            .style('stroke-width', '1px')
            .attr("x1", function(d){
                switch (widthFunc) {
                    case "ratio":
                        return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_ratio==true)[0].x + x_pad + class_padding;
                    case "reward":
                        return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_reward==true)[0].x + x_pad + class_padding;
                    case "cost":
                        return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_cost==true)[0].x + x_pad + class_padding;
                    default:
                        return 0;
                }
            })
            .attr("x2", function(d){
                switch (widthFunc) {
                    case "ratio":
                        return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_ratio==true)[0].x + d.total_width +
                        (d.value-1)*x_pad + x_pad + class_padding;
                    case "reward":
                        return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_reward==true)[0].x + d.total_width +
                        (d.value-1)*x_pad + x_pad + class_padding;
                    case "cost":
                        return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_cost==true)[0].x + d.total_width +
                        (d.value-1)*x_pad + x_pad + class_padding;
                    default:
                        return 0;
                }
            })
            .attr("y1", 0)
            .attr("y2", 0)

            //left hash
            activityAx.append("line")
                .style("stroke", "#707070")
                .style('stroke-width', '1px')
                .attr("x1", function(d){
                    switch (widthFunc) {
                        case "ratio":
                            return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_ratio==true)[0].x + x_pad + class_padding;
                        case "reward":
                            return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_reward==true)[0].x + x_pad + class_padding;
                        case "cost":
                            return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_cost==true)[0].x + x_pad + class_padding;
                        default:
                            return 0;
                    }
                })
                .attr("x2", function(d){
                    switch (widthFunc) {
                        case "ratio":
                            return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_ratio==true)[0].x + x_pad + class_padding;
                        case "reward":
                            return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_reward==true)[0].x + x_pad + class_padding;
                        case "cost":
                            return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_cost==true)[0].x + x_pad + class_padding;
                        default:
                            return 0;
                    }
                })
                .attr("y1", function () {
                    return -dumbell_width/2;
                })
                .attr("y2", function () {
                    return dumbell_width/2;
                })
            //right hash
            activityAx.append("line")
                .style("stroke", "#707070")
                .style('stroke-width', '1px')
                .attr("x1", function(d){
                    switch (widthFunc) {
                        case "ratio":
                            return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_ratio==true)[0].x + d.total_width +
                            (d.value-1)*x_pad + x_pad + class_padding;
                        case "reward":
                            return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_reward==true)[0].x + d.total_width +
                            (d.value-1)*x_pad + x_pad + class_padding;
                        case "cost":
                            return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_cost==true)[0].x + d.total_width +
                            (d.value-1)*x_pad + x_pad + class_padding;
                        default:
                            return 0;
                    }
                })
                .attr("x2", function(d){
                    switch (widthFunc) {
                        case "ratio":
                            return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_ratio==true)[0].x + d.total_width +
                            (d.value-1)*x_pad + x_pad + class_padding;
                        case "reward":
                            return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_reward==true)[0].x + d.total_width +
                            (d.value-1)*x_pad + x_pad + class_padding;
                        case "cost":
                            return activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_cost==true)[0].x + d.total_width +
                            (d.value-1)*x_pad + x_pad + class_padding;
                        default:
                            return 0;
                    }
                })
                .attr("y1", function () {
                    return -dumbell_width/2;
                })
                .attr("y2", function () {
                    return dumbell_width/2;
                })

            activityAx.append("text")
                .style("font-size", containerLabelFontSize)
                .style("fill", "#707070")
                .attr("text-anchor", "middle")
                .attr("x", function(d){
                    let x1, x2, x_pos = 0;
                    switch (widthFunc) {
                        case "ratio":
                            x1 = activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_ratio==true)[0].x + x_pad + class_padding;
                            x2 = activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_ratio==true)[0].x + d.total_width +
                                (d.value-1)*x_pad + x_pad + class_padding;
                            x_pos = x1 + (x2-x1)/2;
                            return x_pos;
                        case "reward":
                            x1 = activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_reward==true)[0].x + x_pad + class_padding;
                            x2 = activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_reward==true)[0].x + d.total_width +
                                (d.value-1)*x_pad + x_pad + class_padding;
                            x_pos = x1 + (x2-x1)/2;
                            return x_pos;
                        case "cost":
                            x1 = activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_cost==true)[0].x + x_pad + class_padding;
                            x2 = activity_dict.filter(x=>x.class==d.class).filter(x=>x.first_flag_cost==true)[0].x + d.total_width +
                                (d.value-1)*x_pad + x_pad + class_padding;
                            x_pos = x1 + (x2-x1)/2;
                            return x_pos;
                        default:
                            return 0;
                    }
                })
                .attr("y", class_padding)
                .attr("dy", "0em")
                .text(function(d) {
                    switch (widthFunc) {
                        case "ratio":
                            return truncateDecimals(activity_dict.filter(x=>x.class==d.class).map(x=>x.ratio).reduce(reducer), 1) + " " +
                            (outline.activityClasses.filter(x=>x.classLabel==d.class)[0].rewards.join(", "))+"/"
                            +outline.activityClasses.filter(x=>x.classLabel==d.class)[0].costs.join(", ");
                        case "reward":
                            return truncateDecimals(activity_dict.filter(x=>x.class==d.class).map(x=>x.reward).reduce(reducer), 1) + " " +
                            outline.activityClasses.filter(x=>x.classLabel==d.class)[0].rewards.join(", ");
                        case "cost":
                            return truncateDecimals(activity_dict.filter(x=>x.class==d.class).map(x=>x.cost).reduce(reducer), 1) + " " +
                            outline.activityClasses.filter(x=>x.classLabel==d.class)[0].costs.join(", ");                   
                        default:
                            return 0;
                    }
                })

        // **************************************************************** //
        // Resource Containers (if any)
        // **************************************************************** //
        let resourceContainerRect = grid.selectAll(".resourceContainerRect")
            .data(res_containers)
            .enter().append("g")
            .attr("transform", function() {
                let xt = classBoxSize/2 + x_ax_pad;
                let yt = classBoxSize*3 + y_ax_pad;
                if (res_containers.length > 0){
                    xt = classBoxSize/2 + x_ax_pad;
                }
                if (act_containers.length > 0){
                    yt = act_containers.length*classBoxSize + classBoxSize*3 + y_ax_pad;
                }
                return "translate("+(xt)+","+(yt)+")"; 
            })

        resourceContainerRect.append('rect')
            .attr("x", 0)
            .attr("y", function (d) {
                return resource_dict.filter(x=>x.name==d.childClassLabel+"_Resource_instance_0")[0].y + class_padding + y_pad + 0.5;
            })
            .attr("width", classBoxSize/2)
            .attr("height", function (d) {
                return d.total_height + (d.num_contained_instances-1)*y_pad - 1;
            })
            .style("fill", res_base_color)
            .style("fill-opacity", container_opacity)   
            .style("stroke", res_base_color)
            // .style('stroke-width', '3px')
            .style('stroke-width', '2px')
            .on('mouseover', function (d) {
                d3.select(this)
                    .style('fill', res_hover_color)
                    .style('stroke', res_hover_color)                
                    .style("fill-opacity", 0.9)   
                div.transition()
                    .duration(200)
                    .style("opacity", 1);
                div.html( "<i><b>"+ d.parentClassName + "</i></b><br/><b>" +
                            "Contained instances: </b><br>"+ d.instanceTable.map(x=>x.parentInstanceName+"<b> -> </b>"+x.childInstanceName + "<br>").join(""))
                    .style("left", (d3.event.layerX) + "px")
                    .style("top",  (d3.event.layerY*1.25) + "px");
            })
            .on('mouseout', function () {
                d3.select(this)
                .style('fill', res_base_color)
                .style('stroke', res_base_color)                
                .style("fill-opacity", container_opacity)   
                div.transition()
                    .duration(500)
                    .style("opacity", 0);
            })
        
        // **************************************************************** //
        // Activity Containers (if any)
        // **************************************************************** //
        // In order to make each container its own box, flatten the <r,a>_containers object arrs
        let flat_act_containers = []
        let placeholder_w = 0
        for (let i=0; i<act_containers.length; i++){
            let ac = act_containers[i];
            let y = (act_containers.length-i-1)*(classBoxSize/2);
            let x, cum_container_x = 0;

            //calculate width
            if (activity_dict.filter(x=>x.name==ac.childClassLabel+"_Activity_instance_0").length>0){
                // if it's a first level container
                let total_width = ac.total_width;
                let d = instances_per_activity_class.filter(x=>x.class==ac.childClassLabel)[0]
                total_width = d.total_width + (d.value-1)*x_pad
                placeholder_w = (total_width/lodash.uniq(ac.instanceTable.map(x=>x.parentInstanceName)).length) - x_pad;
            } else {
                // if it's a multi level container
                var num_levels = i-1;
                var lc = act_containers.filter(x=>x.parentClassLabel == ac.childClassLabel)[0]
                while(num_levels){
                    lc = this.getChild(act_containers, lc.childClassLabel)
                    num_levels--;
                }
                let parentInstanceTable = ac.instanceTable;
                let childContainerWidth = lc.total_width + (lc.num_contained_instances-1)*x_pad;
                let num_contained_instances = lodash.uniq(parentInstanceTable.map(x=>x.childInstanceName)).length
                let total_num_instances = outline.activityInstances.filter(x=>x.classLabel==ac.childClassLabel)[0].instanceTable.length
                let percent_instances_contained = num_contained_instances/total_num_instances
                let total_width = childContainerWidth * percent_instances_contained;
                placeholder_w = (total_width/lodash.uniq(ac.instanceTable.map(x=>x.parentInstanceName)).length) - x_pad;

            }

            // calculate x val
            if (activity_dict.filter(x=>x.name==ac.childClassLabel+"_Activity_instance_0").length>0){
                x = lodash.min(activity_dict.filter(x=>x.class==ac.childClassLabel).map(x=>x.x)) + class_padding  + 1;
            } else {
                num_levels = i-1;
                lc = act_containers.filter(x=>x.parentClassLabel == ac.childClassLabel)[0]
                while(num_levels){
                    lc = this.getChild(act_containers, lc.childClassLabel)
                    num_levels--;
                }
                x = lodash.min(activity_dict.filter(x=>x.class==lc.childClassLabel).map(x=>x.x)) + class_padding  + 1;
            }
            cum_container_x = x + x_pad + x_pad/4;
            for (let ac_name of lodash.uniq(ac.instanceTable.map(x=>x.parentInstanceName))){
                // aci is activity instances contained by current act container
                let aci = ac.instanceTable.filter(x=>x.parentInstanceName==ac_name)
                // let container_instance_w = (aci.length/ac.num_instances) * total_width;
                flat_act_containers.push({
                    parentInstanceName: ac_name,
                    parentClassLabel: ac.parentClassLabel,
                    parentClassName: ac.parentClassName,
                    childInstances: aci.map(x=>x.childInstanceName).join("<br>"),
                    childInstancesArr: aci.map(x=>x.childInstanceName),
                    // total_container_width: total_width*(ac.num_contained_instances/ac.num_instances),
                    x: cum_container_x,
                    y: y,
                    w: placeholder_w,
                })
                cum_container_x = placeholder_w + x_pad + cum_container_x;
            }
        }

        let activityContainerRect = grid.selectAll(".activityContainerRect")
            .data(flat_act_containers.reverse())
            .enter().append("g")
            .attr("transform", function() {
                let xt = classBoxSize*3 + x_ax_pad;
                let yt = 0 + y_ax_pad;
                if (res_containers.length > 0){
                    xt = classBoxSize*4 + x_ax_pad;
                }
                if (act_containers.length > 0){
                    yt = act_containers.length*classBoxSize/2 + y_ax_pad;
                }
                return "translate("+(xt)+","+(yt)+")"; 
            })
        activityContainerRect.append('rect')
            .attr("x", function (d) {
                return d.x;
            })
            .attr("y", function (d) {
                return d.y;
            })
            .attr("height", classBoxSize/2)
            .attr("width", function (d) {
                return d.w;
            })
            .style("fill", act_base_color)
            .style("fill-opacity", 0.3)            
            .style("stroke", act_base_color)
            // .style('stroke-width', '3px')
            .style('stroke-width', '2px')
            .attr("class", function (d) {
                return d.parentInstanceName.replaceAll(" ", "_");
            })
            .on('mouseover', function (d) {
                d.childInstancesArr.forEach(x => {
                    d3.selectAll("."+x.replaceAll(" ","_"))
                        .style('fill', act_hover_color)
                        .style('stroke', act_hover_color)
                        .style('stroke-width', '3px')
                });
                d3.select(this)
                    .style('fill', act_hover_color)
                    .style('stroke', act_hover_color)
                    .style('fill-opacity', 0.9)
                div.transition()
                    .duration(200)
                    .style("opacity", 1);
                div.html("<i><b>"+ d.parentInstanceName + "<br/></i>" +
                            "Contained instances: </b><br>"+ d.childInstances)
                    .style("left", (d3.event.layerX) + "px")
                    .style("top",  (d3.event.layerY*.15) + "px");
            })
            .on('mouseout', function (d) {
                d3.select(this)
                    .style('fill', act_base_color)
                    .style('stroke', act_base_color)
                    .style('fill-opacity', container_opacity)
                d3.selectAll(".activityInstRect") 
                    .style("fill", act_base_color)
                d.childInstancesArr.forEach(x => {
                    d3.selectAll("."+x.replaceAll(" ","_"))
                        .style('fill', act_base_color)
                        .style('stroke', act_base_color)
                        .style('stroke-width', '2px')
                });
                div.transition()
                    .duration(500)
                    .style("opacity", 0);
            })

        // **************************************************************** //
        // Resource Class Boxes
        // **************************************************************** //
        let resourceClassRect = grid.selectAll(".resourceClassRect")
            .data(instances_per_resource_class)
            .enter().append("g")
            .attr("transform", function() {
                let xt = 0 + x_ax_pad;
                let yt = classBoxSize*3 + y_ax_pad;
                if (res_containers.length > 0){
                    xt = classBoxSize + x_ax_pad;
                }
                if (act_containers.length > 0){
                    yt = act_containers.length*classBoxSize + classBoxSize*3 + y_ax_pad;
                }
                return "translate("+(xt)+","+(yt)+")"; 
            })

        resourceClassRect.append('rect')
            .attr("x", 0)
            .attr("y", function (d) {
                return resource_dict.filter(x=>x.name==d.class+"_Resource_instance_0")[0].y + class_padding + y_pad;
            })
            .attr("width", classBoxSize)
            .attr("height", function (d) {
                return d.total_height + (d.value-1)*y_pad;
            })
            .style("fill", res_base_color)
            .style("stroke", res_base_color)
            .style('stroke-width', '1px')
            // commented out fill opacity by how much budget was used
            // .style('stroke-width', '3px')
            // .style("fill-opacity", function (d) {
            //     let total_budget_used = table.filter(x=>x.resource_class==d.class).map(x=>x.budget_used).reduce(reducer);
            //     let total_budget = instances_per_resource_class.filter(x=>x.class==d.class)[0].total_budget;
            //     console.log("fill_opacity ", total_budget_used/total_budget)
            //     return total_budget_used/total_budget;
            // })
            .on('mouseover', function (d) {
                let total_budget_used = table.filter(x=>x.resource_class==d.class).map(x=>x.budget_used).reduce(reducer);
                let res_class_info = outline.resourceClasses.filter(x=>x.classLabel==d.class)[0];
                let total_budget = instances_per_resource_class.filter(x=>x.class==d.class)[0].total_budget;
                d3.select(this)
                    .style('fill', res_hover_color)
                    .style('stroke', res_hover_color)
                div.transition()
                    .duration(200)
                    .style("opacity", 1);
                div.html("<i><b>"+res_class_info.className+"</i></b>"+"<br>"+
                    "<b><i>"+(truncateDecimals(total_budget_used/total_budget, 2)*100)+"% "+ d.budget_unit +" allocated</i></b><br><br>"+
                    truncateDecimals(total_budget_used, 2)+" "+ d.budget_unit +" allocated<br>"+
                    truncateDecimals(total_budget, 2)+" "+ d.budget_unit +" budgeted<br>"
                )
                    .style("left", (d3.event.layerX) + "px")
                    .style("top",  (d3.event.layerY*1.25) + "px");
            })
            .on('mouseout', function () {
                d3.select(this)
                    .style("stroke", res_base_color)
                    .style('fill', res_base_color)                    
                div.transition()
                    .duration(500)
                    .style("opacity", 0);
            })

        resourceClassRect.append("text")
            .style("font-size", classLabelFontSize)
            .style("font-weight", classLabelFontStyle)
            .attr("x", 0)
            .attr("y", function (d) {
                return resource_dict.filter(x=>x.name==d.class+"_Resource_instance_0")[0].y + class_padding;
            })
            .text(function(d) { return d.class; })
            .style("fill", "#707070")
        
        let resourceClassSummary = summary.selectAll(".resourceClassSummary")
            .data(instances_per_resource_class)
            .enter().append("g")
        
        let explainer_html = "";

        resourceClassSummary.append("text")
            .style("font-size", "24px")
            .style("font-weight", classLabelFontStyle)
            .attr("x", 0)
            .attr("y", function (d, i) {
                return i*50;
            })
            .attr("dy", "0em")
            .text(function(d) {
                let total_budget_used = table.filter(x=>x.resource_class==d.class).map(x=>x.budget_used).reduce(reducer);
                let res_class_info = outline.resourceClasses.filter(x=>x.classLabel==d.class)[0];
                let total_budget = instances_per_resource_class.filter(x=>x.class==d.class)[0].total_budget;
                explainer_html = explainer_html.concat("<i><b>"+res_class_info.className+"</i></b>"+"<br>"+
                    ""+(truncateDecimals(total_budget_used/total_budget, 2)*100)+"% "+ d.budget_unit +" allocated<br><br><br>")
            })
        
        $("#soln-explainer").html(explainer_html)

        // **************************************************************** //
        // Resource Instance Boxes
        // **************************************************************** //
        let resourceInstRect = grid.selectAll(".resourceInstRect")
            .data(resource_dict)
            .enter().append("g")
            .attr("transform", function() {
                let xt = 0 + x_ax_pad;
                let yt = classBoxSize*3 + y_ax_pad;
                if (res_containers.length > 0){
                    xt = classBoxSize + x_ax_pad;
                }
                if (act_containers.length > 0){
                    // yt = classBoxSize*4 + y_ax_pad;
                    yt = act_containers.length*classBoxSize + classBoxSize*3 + y_ax_pad;
                }
                return "translate("+(xt)+","+(yt)+")"; 
            })

        resourceInstRect.append('rect')
            .attr("x", function () {
                return classBoxSize + x_pad;
            })
            .attr("y", function (d) {
                return table.filter(x=>((x.resource==d.name)&&(x.row==d.row)))[0].y;
            })
            .attr("width", classBoxSize)
            .attr("height", function (d) {
                return d.instance_height;
            })
            .style("fill", res_base_color)
            .style("stroke", res_base_color)
            .style('stroke-width', '1px')
            .style("fill-opacity", function(d){
                let total_budget_used_this_instance = table.filter(x=>x.resource==d.name).map(x=>x.budget_used).reduce(reducer)
                return total_budget_used_this_instance/d.budget
            })
            .on('mouseover', function (d) {
                let total_budget_used_this_instance = table.filter(x=>x.resource==d.name).map(x=>x.budget_used).reduce(reducer)
                d3.select(this)
                    .style('fill', res_hover_color)
                div.transition()
                    .duration(200)
                    .style("opacity", 1);
                div.html("<i><b>"+d.original_name+"</i></b>"+"<br>"+
                    "<b><i>"+(truncateDecimals(total_budget_used_this_instance/d.budget, 2)*100)+"% "+ d.budget_unit +" allocated</i></b><br><br>"+
                    truncateDecimals(total_budget_used_this_instance, 2)+" "+ d.budget_unit +" allocated<br>"+
                    d.budget+" "+ d.budget_unit +" budgeted<br>"
                )
                .style("left", (d3.event.layerX) + "px")
                .style("top",  (d3.event.layerY) + "px");
            })
            .on('mouseout', function () {
                d3.select(this)
                    .style('fill', res_base_color)
                div.transition()
                    .duration(500)
                    .style("opacity", 0);
            })
        
        resourceInstRect.append("text")
            .style("font-size", instanceLabelFontSize)
            .attr("x", function () {
                return classBoxSize*2 + lodash.max([x_pad*1.5, 8]);
            })
            .attr("y", function (d) {
                return table.filter(x=>((x.resource==d.name)&&(x.row==d.row)))[0].y + y_pad;
            })
            .text(function(d) { return d.instance; })
            .style("fill", "#707070")

        // **************************************************************** //
        // Activity Class Boxes
        // **************************************************************** //
        let activityClassRect = grid.selectAll(".activityClassRect")
            .data(instances_per_activity_class)
            .enter().append("g")
            .attr("transform", function() {
                let xt = classBoxSize*4 + x_pad + x_ax_pad;
                // xt = classBoxSize*4 + x_pad + x_ax_pad;
                let yt = 0 + y_ax_pad;
                if (res_containers.length > 0){
                    xt = classBoxSize*5 + x_pad + x_ax_pad;
                    // xt = classBoxSize*5 + x_pad + x_ax_pad;
                }
                if (act_containers.length > 0){
                    // yt = classBoxSize + y_ax_pad;
                    yt = act_containers.length*(classBoxSize) + y_ax_pad;
                }
                return "translate("+(xt)+","+(yt)+")"; 
            })

        activityClassRect.append('rect')
            .attr("x", function (d) {
                return lodash.min(activity_dict.filter(x=>x.class==d.class).map(x=>x.x));
            })
            .attr("y", 0)
            .attr("width", function (d) {
                return d.total_width + (d.value-1)*x_pad;
            })
            .attr("height", classBoxSize)
            .style("fill", '#F1EFE9')
            .style("stroke", '#F1EFE9')
            .style('stroke-width', '1px')
            .on('mouseover', function (d) {
                let act_class_info = outline.activityClasses.filter(x=>x.classLabel==d.class)[0];
                d3.select(this)
                    .style('fill', act_hover_color)
                    .style('stroke', act_hover_color)
                div.transition()
                    .duration(200)
                    .style("opacity", 1);
                div.html("<i><b>"+act_class_info.className+"</i></b>"+"<br>"
                )
                    .style("left", (d3.event.layerX) + "px")
                    .style("top",  (d3.event.layerY*1.25) + "px");
            })
            .on('mouseout', function () {
                d3.select(this)
                    .style("stroke", act_base_color)
                    .style('fill', act_base_color)                    
                div.transition()
                    .duration(500)
                    .style("opacity", 0);
            })

        activityClassRect.append("text")
            .style("font-size", classLabelFontSize)
            .style("font-weight", classLabelFontStyle)
            .attr("x", function (d) {
                return lodash.min(activity_dict.filter(x=>x.class==d.class).map(x=>x.x)) + x_pad;
            })
            .attr("y", function () {
                return classBoxSize/2 + 2;
            })
            .text(function(d) { return d.class; })
            .style("fill", "#707070")

        // **************************************************************** //
        // Activity Instance Boxes
        // **************************************************************** //
        let activityInstRect = grid.selectAll(".activityInstRect")
            .data(activity_dict)
            .enter().append("g")
            .attr("transform", function() {
                let xt = classBoxSize*4 + x_ax_pad;
                let yt = 0 + y_ax_pad;
                if (res_containers.length > 0){
                    xt = classBoxSize*5 + x_ax_pad;
                }
                if (act_containers.length > 0){
                    yt = act_containers.length*(classBoxSize) + y_ax_pad;
                }
                return "translate("+(xt)+","+(yt)+")"; 
            })

        activityInstRect.append('rect')
            .attr("x", function (d) {
                return table.filter(x=>((x.activity==d.name)&&(x.col==d.col)))[0].x - classBoxSize;
            })
            .attr("y", function () {
                return classBoxSize + y_pad; 
            })
            .attr("width", function (d) {
                return d.instance_width;
            })
            .attr("class", function (d) {
                return d.original_name.replaceAll(" ", "_");
            })
            .attr("fill-opacity", function (d) {
                return d.selected+0.2;
            })
            .attr("height", classBoxSize)
            .style("fill", '#F1EFE9')
            .style("stroke", '#F1EFE9')
            .style('stroke-width', '1px')
            .on('mouseover', function (d) {
                d3.select(this)
                    .style('fill', act_hover_color)
                    .style('stroke', act_hover_color)
                div.transition()
                    .duration(200)
                    .style("opacity", 1);
                div.html("<i><b>"+d.original_name+"</i></b>"+"<br>"+
                "<b>Total reward:</b> "+d.reward+"<br>"+
                "<b>Total cost:</b> "+d.cost+" "+d.cost_unit.join(", ")
                )
                    .style("left", (d3.event.layerX) + "px")
                    .style("top",  (d3.event.layerY*1.25) + "px");
            })
            .on('mouseout', function () {
                d3.select(this)
                    .style("stroke", act_base_color)
                    .style('fill', act_base_color)                    
                div.transition()
                    .duration(500)
                    .style("opacity", 0);
            })
        
        activityInstRect.append("text")
            .style("font-size", instanceLabelFontSize)
            .attr("x", function (d) {
                return table.filter(x=>((x.activity==d.name)&&(x.col==d.col)))[0].x - classBoxSize;
            })
            .attr("y", function () {
                return classBoxSize*2 + lodash.max([y_pad*2.5, 15]);
            })
            .text(function(d) {
                return !isNaN(+(d.original_name.split("_").slice(-1)[0])) ? d.original_name.split("_").slice(-1)[0] : d.instance;
            })
            .style("fill", "#707070")

        // **************************************************************** //    
        // Allocation (Resource * Activity) boxes to fill out matrix
        // **************************************************************** //
        grid.selectAll(".allocRect")
            .data(table)
            .enter().append('rect')
            .attr("transform", function() {
                let xt = classBoxSize*3 + x_ax_pad;
                let yt = classBoxSize*3 + y_ax_pad;
                if (res_containers.length > 0){
                    xt = classBoxSize*4 + x_ax_pad;
                }
                if (act_containers.length > 0){
                    // yt = classBoxSize*4 + y_ax_pad;
                    yt = classBoxSize*2 + (act_containers.length+1)*(classBoxSize) + y_ax_pad;
                }
                return "translate("+(xt)+","+(yt)+")"; 
            })
            .attr("x", function (d) {
                let alloc_classes = outline.resourceClasses.filter(x=>x.classLabel==d.resource_class)[0].canBeAllocatedToClasses;
                let this_act = outline.activityClasses.filter(x=>x.classLabel==d.activity_class)[0].className;
                return (alloc_classes.includes(this_act) ? d.x : undefined);
            })
            .attr("y", function (d) {
                let alloc_classes = outline.resourceClasses.filter(x=>x.classLabel==d.resource_class)[0].canBeAllocatedToClasses;
                let this_act = outline.activityClasses.filter(x=>x.classLabel==d.activity_class)[0].className;
                return (alloc_classes.includes(this_act) ? d.y : undefined);
            })
            .attr("width", function (d) {
                let alloc_classes = outline.resourceClasses.filter(x=>x.classLabel==d.resource_class)[0].canBeAllocatedToClasses;
                let this_act = outline.activityClasses.filter(x=>x.classLabel==d.activity_class)[0].className;
                return (alloc_classes.includes(this_act) ? d.w : undefined);
            })
            .attr("height", function (d) {
                return d.h;
            })
            .style("fill", '#9DB398')
            .style("stroke", '#9DB398')
            .style('stroke-width', alloc_rect_stroke)
            .style("fill-opacity", function (d) {
                return d.fill_opacity>0 ? 0.1+Math.log1p(d.fill_opacity) : d.fill_opacity;
            })
            .on('mouseover', function (d) {
                d3.select(this)
                    .style('stroke', '#9DB398')
                    .style('stroke-width', '2px')
                    .style('border', 'solid #9DB398')
                div.transition()
                    .duration(200)
                    .style("opacity", 1);
                div.html( "<b>"+
                            "Resource: </b>"+resource_name_label_map.filter(x=>x.label==d.resource)[0].original_name+ "<br/><b>" +
                            "Activity: </b>"+activity_name_label_map.filter(x=>x.label==d.activity)[0].original_name+ "<br/><b>" +
                            // "Activity: </b>"+d.activity + "<br/><b>"+
                            "Budget allocated: </b>"+d.budget_used+" / "+d.total_resource_budget)
                    .style("left", (d3.event.layerX) + "px")
                    .style("top",  (d3.event.layerY) + "px");
            })
            .on('mouseout', function () {
                d3.select(this)
                    .style('stroke', '#9DB398')
                    .style('stroke-width', alloc_rect_stroke)
                    .style('border', 'solid #9DB398')
                div.transition()
                    .duration(500)
                    .style("opacity", 0);
            })
    }

    inheritContainerRewards(classLabel, instanceName, containerList, outlineInstances, cumReward){
        let containerClass = undefined;
        let instReward = 0;
        containerClass = containerList.filter(x=>x.childClassLabel==classLabel)[0]
        if (containerClass!= undefined){
            // Get contained instances by looking up in instanceTable of container object
            let containingTable = containerClass.instanceTable;
            let containedInstances = containingTable.filter(x=>x.childInstanceName==instanceName)
            let parentClassLabel = containerClass.parentClassLabel
            // Get those containingInstances rewards
            for (let i=0; i<containedInstances.length; i++){
                let parentInstanceName = containedInstances[i].parentInstanceName;
                let parentClassInstanceTable = outlineInstances.filter(x=>x.classLabel==parentClassLabel)[0].instanceTable
                instReward = parentClassInstanceTable.filter(x=>x.instanceName==parentInstanceName)[0].reward
                cumReward = cumReward + instReward
                cumReward = this.inheritContainerRewards(containerClass.parentClassLabel, parentInstanceName, containerList, outlineInstances, cumReward)
            }
        } else{
            return cumReward
        }
        return cumReward
    }

    // **************************************************************** //
    // Helper functions
    // **************************************************************** //
    truncateDecimals(number, digits) {
        var multiplier = Math.pow(10, digits),
            adjustedNum = number * multiplier,
            truncatedNum = Math[adjustedNum < 0 ? 'ceil' : 'floor'](adjustedNum);

        return truncatedNum / multiplier;
    }

    groupBy(key) {
        return function group(array) {
        return array.reduce((acc, obj) => {
            const property = obj[key];
            acc[property] = acc[property] || [];
            acc[property].push(obj);
            return acc;
        }, {});
        };
    }
    getChild(act_containers, childClassLabel){
        return act_containers.filter(x=>x.parentClassLabel == childClassLabel)[0];
    }

    get_pad(instance_dict){
        let x_pad_dict = [
            {
                num_inst: 0,
                pad: 8,
            },
            {
                num_inst: 0,
                pad: 5,
            },
            {
                num_inst: 40,
                pad: 3,
            },
            {
                num_inst: 60,
                pad: 3,
            }

        ]
        let diffs =  x_pad_dict.map(x=>Math.abs(x.num_inst-instance_dict.length))
        return x_pad_dict[diffs.indexOf(lodash.min(diffs))].pad
    }
    get_class_pad(x_pad){
        let d = [
            {
                pad: 8,
                w: 24,
            },
            {
                pad: 5,
                w: 20,
            },
            {
                pad: 3,
                w: 18
            },
        ]
        let diffs =  d.map(x=>Math.abs(x.pad-x_pad))
        return d[diffs.indexOf(lodash.min(diffs))].w
    }
    get_class_box_size(x_pad){
        let b = this.get_class_pad(x_pad)
        return b
    }
}