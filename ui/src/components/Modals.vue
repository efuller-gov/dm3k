
<template>
    <div>
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
            <button id="add-row">Add instance row</button>
          </div>
            <div id="modal-instance-table" class="instance-table"></div>
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

export default {
    name: 'Modals',
    mounted(){
        this.$root.$on('show-instance-modal', e => {
            console.log("-- IN Modals vue e: ", e)
            this.showInstanceModal(e)
        })
    },
    methods:{
        closeModal(){
			let modal = document.querySelector(".modal")
			modal.style.display = "none"
		},
        showInstanceModal(event){
            console.log("IN SHOW INSTANACE MODAL. Event: ", event)
            let cellId = event.detail.id;
            let cellName = event.detail.name;
            let cellType = event.detail.type;   // 'Resource'  or 'Activity' or 'Contains' or 'AllocatedTo'
            let eventDetail = event.detail
            let instanceType = cellId;
            let instanceName = cellName;
            let resOrAct = cellType;
            let budgetName = event.detail.budget;
            let rewardName = event.detail.reward;
            let costName = event.detail.cost;
            
            // TODO: replace this dependence on graph with reference to $store
            // let graph = this.dm3kgraph;
        
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
                this.showModal(
                    instanceType,
                    instanceName,
                    resOrAct,
                    budgetName,
                    rewardName,
                    costName,
                    eventDetail)
            }
        },
        showModal(instanceType, instanceName, resOrAct, budgetName, rewardName, costName, details){
            console.log(budgetName, rewardName, costName, details)
            //get data table for the selected res or act type
            let modal = document.querySelector(".modal")
            $('#alloc-selector').hide()
            modal.style.display = "block"
            modal.style.display = "block"
            let titleText = ''

            // let modalInstanceName = instanceName

            if (resOrAct == 'Activity' || resOrAct == 'activity'){
                //Columns are Instance | Reward | Cost
                titleText = "<p>"+instanceName + ", " + instanceType+"</p>You can define any number of <b>" + instanceName + "'s</b>, a <b>"+instanceType+" activity</b>. " +
                "You may also assign each instance with a <b>cost</b> and a <b>reward</b>."
                $('#add-row').text('Add activity instance')
                // tabledata = graph.activityInstances.filter(x => x.label == instanceName)[0].instanceTableData;
                // tablecols = [
                //         {title: "", formatter:minusButton, width:5, hozAlign:"center", cellClick:
                //             function(e, cell){
                //             let label = cell.getRow().getData().name
                //             removeRow(label)}
                //         },
                //         {title: instanceName+" instance name", field:"name", editor:"input"},
                //     ]
                // for (let c of costName) {
                //     tablecols.push({title:"Cost ("+c+")", field:"cost_"+c, hozAlign:"left", sorter:"number", editor:"input"})
                // }
                // if (rewardName != '') {
                //     tablecols.push({title:"Reward ("+rewardName+")", field:"reward", hozAlign:"left", sorter:"number", editor:"input"})
                // }
            }
            if (resOrAct == 'Resource' || resOrAct == 'resource'){
                //Columns are Instance | Cost
                titleText = "<p>"+instanceName + ", " + instanceType+"</p>You can define any number of <b>" + instanceName + "'s</b>, a <b>"+instanceType+" resource</b>. You may also assign each instance with a <b>budget</b> amount."
                $('#add-row').text('Add resource instance')
                // Get tabledata for this resource from the graph
                // tabledata = graph.resourceInstances.filter(x => x.label == instanceName)[0].instanceTableData;
                // // console.log("Table Data: %O", tabledata)
                // tablecols = [
                //         {title: "", formatter:minusButton, width:5, hozAlign:"center", cellClick:
                //             function(e, cell){
                //             let label = cell.getRow().getData().name
                //             removeRow(label)}
                //         },
                //         {title: instanceName + " instance name", field:"name", editor:"input"}]
                // for (let b of budgetName) {
                //     tablecols.push({title:"Budget ("+b+")", field:"budget_"+b, hozAlign:"left", sorter:"number", editor:"input"})
                // } 
            }
            
            // Make it easier to add activities and resources
            // modalTableName = instanceName+"_"+resOrAct+"_instance";

            // let lastEntryArray = tabledata[tabledata.length-1].name.split("_");
            // modalTableNameCnt = parseInt(lastEntryArray[lastEntryArray.length - 1]);

            // table = new Tabulator("#modal-instance-table", {
            //         height:TABLEHEIGHT,
            //         addRowPos:"bottom",
            //         reactiveData: true,
            //         data: tabledata,
            //         layout:TABLELAYOUT,
            //         columns:tablecols,
            // });
            $('#table-title').html(titleText)
            // return table
        }
    }
}
</script>

<style scoped>

</style>