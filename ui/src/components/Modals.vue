
<template>
    <div>
        <link href="https://unpkg.com/tabulator-tables@4.4.1/dist/css/tabulator.min.css" rel="stylesheet">
        <div class="modal">
        <span @click="closeModal" class="close-btn">&times;</span>
        <div class="modal-header">
        </div>
        <div class="modal-content">
          <div id="table-left-aligned-content">
            <div id="table-title"></div>
          </div>
          <div id="table-and-control-buttons-container">
          <div id="instance-table-control-buttons">
            <button @click="addRow" id="add-row">Add instance row</button>
          </div>
            <div ref="table" id="modal-instance-table" class="instance-table"></div>
		</div>
        </div>
        <div class="modal-footer">
        </div>
			</div>
			<div id="soln-modal" class="soln-modal">
				<span class="close-btn" onclick="closeSolnModal()">&times;</span>
				<div class="modal-content">
					<img id='soln-explainer-graphic' onclick="location.href='./'" src="../assets/output-explainer.png">
					<p id="soln-title">Optimal Allocation Plan</p>
					<button id="soln-explainer-btn" onclick="toggleSolnGraphicExplainer()">Show me how to read this</button>
					<div id="soln-table-top-aligned-content">
						Size and sort activity instance columns by
						<select class="chosen-select" id="widthFunctionToggle">
							<option value="cost">cost</option>
							<option value="ratio">reward / cost ratio</option>
							<option value="reward">reward</option>
						</select>
					</div>
					<div id="soln-visualization"></div>
				</div>
				<div class="modal-footer">
				</div>
      </div>
    </div>
</template>

<script>
import $ from 'jquery'
// var Tabulator = require("tabulator-tables"); //import Tabulator library
import Tabulator from "tabulator-tables"

export default {
    name: 'Modals',
    mounted(){
        this.$root.$on('show-instance-modal', e => {
            this.showInstanceModal(e)
        })
    },
    data(){
        return{
           TABLEHEIGHT :  "300px",
           TABLELAYOUT : "fitColumns",
           instanceName : []
        }
    },
    methods:{
        minusButton(){
            return "<span class='remove-button-class'></span>";
        },
        addRow(e){
            console.log("---> addRow e: ", e)
            if ($('#add-row').text().includes('resource')){
                let resOrAct = 'Resource'
                let modalTableName = this.instanceName+"_"+resOrAct+"_instance";
                // let lastEntryArray = tabledata[tabledata.length-1].name.split("_");
                // let modalTableNameCnt = parseInt(lastEntryArray[lastEntryArray.length - 1]);
                // modalTableNameCnt += 1
                let modalTableNameCnt = 1;
                let newName = modalTableName +"_"+modalTableNameCnt;
                // let instanceName = modalInstanceName;
                // let resourceInstance = this.dm3kgraph.getResourceInstance(instanceName);
                console.log("before", this.$store.state.resourceInstances)
                let resourceInstance = this.$store.state.resourceInstances.filter(x=>x.name==this.instanceName);
                console.log("retreived resourceInstance ", resourceInstance)
                resourceInstance.addDefaultRow(newName);
                console.log("updated resourceInstance", resourceInstance)
                this.$store.commit('addResourceInstance', resourceInstance)
                console.log("after", this.$store.state.resourceInstances)

            }
            // if ($('#add-row').text().includes('allocation')) {
            //     tabledata.push({resourceInstance: "ALL", activityInstance: 'ALL'})
            // }
            // if ($('#add-row').text().includes('contains')){
            //     tabledata.push({parentInstance: "ALL", childInstance: 'ALL'});
            // }
            // if ($('#add-row').text().includes('activity')){
            //     let resOrAct = 'Activity'
            //     let modalTableName = instanceName+"_"+resOrAct+"_instance";
			//     let lastEntryArray = tabledata[tabledata.length-1].name.split("_");
			//     let modalTableNameCnt = parseInt(lastEntryArray[lastEntryArray.length - 1]);
            //     modalTableNameCnt += 1
            //     let newName = modalTableName +"_"+modalTableNameCnt;
            //     let instanceName = modalInstanceName;
            //     let activityInstance = dm3kgraph.getActivityInstance(instanceName);
            //     activityInstance.addDefaultRow(newName)
            // }
        },
        removeRow(label, tabledata){
            // TO DO: this won't work. Needs to access store.
            tabledata.pop(tabledata.filter(x=>x.label==label))
        },
        closeModal(){
			let modal = document.querySelector(".modal")
			modal.style.display = "none"
		},
        showInstanceModal(event){
            console.log("IN SHOW INSTANACE MODAL. Event: ", event)
            let cellId = event.detail.id;
            let cellName = event.detail.name;
            let cellType = event.detail.type;   // 'Resource'  or 'Activity' or 'Contains' or 'AllocatedTo'
            // let eventDetail = event.detail
            let instanceType = cellId;
            let instanceName = cellName;
            let resOrAct = cellType;
            let budgetName = event.detail.budget;
            let rewardName = event.detail.reward;
            let costName = event.detail.cost;
            
            if (cellType.includes('AllocatedTo')){
                resOrAct = 'allocation'
                let resourceName = cellName.split('_')[0]
                let activityName = cellName.split('_')[1]
                this.showAllocationModal(
                    instanceType,
                    instanceName,
                    resOrAct,
                    budgetName,
                    rewardName,
                    costName,
                    resourceName,
                    activityName)
            } else if (cellType.includes('Contains')) {
                resOrAct = 'contains'
                let parentName = cellName.split('_')[0]
                let childName = cellName.split('_')[1]
                this.showContainsModal(
                    instanceType,
                    instanceName,
                    resOrAct,
                    budgetName,
                    rewardName,
                    costName,
                    parentName,
                    childName)
            } else{
                this.showActResModal(
                    instanceType,
                    instanceName,
                    resOrAct,
                    budgetName,
                    rewardName,
                    costName)
            }
        },
        showActResModal(instanceType, instanceName, resOrAct, budgetName, rewardName, costName){
            let tablecols = [];
            let tabledata = [];
        
            //get data table for the selected res or act type
            let modal = document.querySelector(".modal")
            $('#alloc-selector').hide()
            modal.style.display = "block"
            modal.style.display = "block"
            let titleText = ''
            this.instanceName = instanceName

            // let modalInstanceName = instanceName

            if (resOrAct == 'Activity' || resOrAct == 'activity'){
                //Columns are Instance | Reward | Cost
                titleText = "<p>"+instanceName + ", " + instanceType+"</p>You can define any number of <b>" + instanceName + "'s</b>, a <b>"+instanceType+" activity</b>. " +
                "You may also assign each instance with a <b>cost</b> and a <b>reward</b>."
                $('#add-row').text('Add activity instance')
                tabledata = this.$store.state.activityInstances.filter(x => x.label == instanceName)[0].instanceTableData;
                tablecols = [
                        {title: "", formatter:this.minusButton, width:5, hozAlign:"center", cellClick:
                            function(e, cell){
                            let label = cell.getRow().getData().name
                            this.removeRow(label, tabledata)}
                        },
                        {title: instanceName+" instance name", field:"name", editor:"input"},
                    ]
                for (let c of costName) {
                    tablecols.push({title:"Cost ("+c+")", field:"cost_"+c, hozAlign:"left", sorter:"number", editor:"input"})
                }
                if (rewardName != '') {
                    tablecols.push({title:"Reward ("+rewardName+")", field:"reward", hozAlign:"left", sorter:"number", editor:"input"})
                }
            }
            if (resOrAct == 'Resource' || resOrAct == 'resource'){
                //Columns are Instance | Cost
                titleText = "<p>"+instanceName + ", " + instanceType+"</p>You can define any number of <b>" + instanceName + "'s</b>, a <b>"+instanceType+" resource</b>. You may also assign each instance with a <b>budget</b> amount."
                $('#add-row').text('Add resource instance')
                // Get tabledata for this resource from the graph
                tabledata = this.$store.state.resourceInstances.filter(x => x.label == instanceName)[0].instanceTableData;
                tablecols = [
                        {title: "", formatter:this.minusButton, width:5, hozAlign:"center", cellClick:
                            function(e, cell){
                            let label = cell.getRow().getData().name
                            this.removeRow(label, tabledata)}
                        },
                        {title: instanceName + " instance name", field:"name", editor:"input"}]
                for (let b of budgetName) {
                    tablecols.push({title:"Budget ("+b+")", field:"budget_"+b, hozAlign:"left", sorter:"number", editor:"input"})
                } 
            }
            
            // Make it easier to add activities and resources
            // modalTableName = instanceName+"_"+resOrAct+"_instance";
            // let lastEntryArray = tabledata[tabledata.length-1].name.split("_");
            // modalTableNameCnt = parseInt(lastEntryArray[lastEntryArray.length - 1]);

                    new Tabulator(this.$refs.table, {
                    height:this.TABLEHEIGHT,
                    addRowPos:"bottom",
                    reactiveData: true,
                    data: tabledata,
                    layout:this.TABLELAYOUT,
                    columns:tablecols,
            });
            $('#table-title').html(titleText)
        },
        showAllocationModal(instanceType, instanceName, resOrAct, budgetName, rewardName, costName, resourceName, activityName){
            console.log("--> Show ALLOCATION modal")
            //get data table for the selected res or act type
            $('#alloc-selector').show()
            $('#add-row').text('Add allocation between instances')
            let modal = document.querySelector(".modal")
            modal.style.display = "block"
            modal.style.display = "block"

            let titleText = ''
            //Columns are Instances of resources | Dropdowns for all available instances of activities
            titleText = "Allocated individual resource instances of <b> " + resourceName + " </b>to activity instances of <b>" + activityName + "</b>."
            let res_tabledata = this.$store.state.resourceInstances.filter(x => x.label == resourceName)[0].instanceTableData;
            let act_tabledata = this.$store.state.activityInstances.filter(x => x.label == activityName)[0].instanceTableData;
            let resource_instances = res_tabledata.map(x => x.name)
            let activity_instances = act_tabledata.map(x => x.name)
            resource_instances.push('ALL')
            activity_instances.push('ALL')
            
            //tabledata = res_tabledata;
            // TODO: How am I going to lookup allocations from here?
            // let tabledata = graph.getAllocatedToInstance(resourceName, activityName).instanceTableData;
            let tabledata = []

            let tablecols = [
                    {title: "", formatter:this.minusButton, width:5, hozAlign:"center", cellClick:
                        function(e, cell){
                        let label = cell.getRow().getData().name
                        this.removeRow(label, tabledata)}
                    },
                    {title: "resource type: "+resourceName, field:"resourceInstance", width:200, editor:"select",
                        editorParams: {
                            values: resource_instances,
                            defaultValue:"ALL", //set the value that should be selected by default if the cells value is undefined
                            verticalNavigation:"hybrid"}},
                    {title: "activity type: "+activityName, field:"activityInstance", width:200, hozAlign:"left",
                        editor:"select",
                        editorParams: {
                            values: activity_instances,
                            defaultValue:"ALL", //set the value that should be selected by default if the cells value is undefined
                            verticalNavigation:"hybrid"},
                    }
                ]
            new Tabulator("#modal-instance-table", {
                    height:this.TABLEHEIGHT,
                    addRowPos:"bottom",
                    reactiveData: true,
                    data: tabledata,
                    layout:this.TABLELAYOUT,
                    columns:tablecols,
            });
            $('#table-title').html(titleText)
        }
    }
}
</script>

<style scoped>
  </style