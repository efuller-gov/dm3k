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
            <span class="close-btn" @click="closeSolnModal()">&times;</span>
            <div class="modal-content">
                <img id='soln-explainer-graphic' onclick="location.href='./'" src="../assets/output-explainer.png">
                <p id="soln-title">Optimal Allocation Plan</p>
                <button @click="toggleSolnGraphicExplainer()" id="soln-explainer-btn">Show me how to read this</button>
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
import Tabulator from "tabulator-tables"
import {
    Dm3kSolutionVis
} from '../js/dm3ksolution/dm3kSolutionVis';

export default {
    name: 'Modals',
    mounted() {
        this.solnVis = new Dm3kSolutionVis()
        this.$root.$on('show-instance-modal', e => {
            this.showInstanceModal(e)
        })

        this.$root.$on('show-solution-modal', e => {
            this.showSolutionModal(e.body, e.outputJson)
        })
    },
    data() {
        return {
            solnVis: {},
            TABLEHEIGHT: "300px",
            TABLELAYOUT: "fitColumns",
            instanceName: [],
            resourceName: [],
            activityName: [],
            parentName: [],
            childName: [],
            xIcon: require("../assets/x-icon.svg"),
        }
    },
    methods: {
        toggleSolnGraphicExplainer(){
            $('#soln-explainer-graphic').toggle()
            $('#soln-visualization').toggle()
            if ($('#soln-explainer-btn').hasClass('enabled')){
                $('#soln-explainer-btn').removeClass('enabled')
                $('#soln-explainer-btn').html('Show me how to read this')
            } else{
                $('#soln-explainer-btn').addClass('enabled')
                $('#soln-explainer-btn').html('Hide')
            }
        },
        addRow() {
            if ($('#add-row').text().includes('resource')) {
                // let resourceInstance = this.$store.state.resourceInstances.filter(x=>x.label == this.instanceName)[0];
                let resourceInstance = this.$store.state.dm3kGraph.resourceInstances.filter(x => x.label == this.instanceName)[0];
                let newName = this.instanceName + "_Resource_instance_" + resourceInstance.instanceTableData.length;
                let instanceExample = {
                    name: newName
                };
                let budgetNameList = resourceInstance.budgetNameList;
                for (let budgetName of budgetNameList) {
                    instanceExample["budget_" + budgetName] = 1;
                }
                this.$store.commit('addResourceInstance', {
                    instanceName: this.instanceName,
                    newInstance: instanceExample
                })
            }
            if ($('#add-row').text().includes('allocation')) {
                this.$store.commit('addCanBeAllocatedTo', {
                    existingResName: this.resourceName,
                    actName: this.activityName
                })
            }
            if ($('#add-row').text().includes('contains')){
                // tabledata.push({parentInstance: "ALL", childInstance: 'ALL'});
                this.$store.commit('addContainsInstance', {
                    parentName: this.parentName,
                    childName: this.childName
                })
            }
            if ($('#add-row').text().includes('activity')) {
                let activityInstance = this.$store.state.dm3kGraph.activityInstances.filter(x => x.label == this.instanceName)[0];
                let newName = this.instanceName + "_Activity_instance_" + activityInstance.instanceTableData.length;
                let instanceExample = {
                    name: newName,
                    reward: 1
                };
                for (const costName of activityInstance.costNameList) {
                    instanceExample["cost_" + costName] = 1;
                }
                this.$store.commit('addActivityInstance', {
                    instanceName: this.instanceName,
                    newInstance: instanceExample
                })
            }
        },
        closeModal() {
            let modal = document.querySelector(".modal")
            modal.style.display = "none"
        },
        closeSolnModal() {
            let modal = document.querySelector(".soln-modal")
            modal.style.display = "none"
            $('#menu').toggleClass('shrink')
            if ($('#menu').hasClass('shrink')) {
                $('#hide-worksheet-button').html('Expand worksheet')
            } else {
                $('#hide-worksheet-button').html('Hide worksheet')
            }
        },
        showInstanceModal(event) {
            let cellId = event.detail.id;
            let cellName = event.detail.name;
            let cellType = event.detail.type; // 'Resource'  or 'Activity' or 'Contains' or 'AllocatedTo'
            let instanceType = cellId;
            let instanceName = cellName;
            let resOrAct = cellType;
            let budgetName = event.detail.budget;
            let rewardName = event.detail.reward;
            let costName = event.detail.cost;

            if (cellType.includes('AllocatedTo')) {
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
            } else {
                this.showActResModal(
                    instanceType,
                    instanceName,
                    resOrAct,
                    budgetName,
                    rewardName,
                    costName)
            }
        },
        showActResModal(instanceType, instanceName, resOrAct, budgetName, rewardName, costName) {

            function removeRow(label) {
                let ind = tabledata.findIndex(x => x.name == label)
                tabledata.splice(ind, 1)
            }
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

            if (resOrAct == 'Activity' || resOrAct == 'activity') {
                //Columns are Instance | Reward | Cost
                titleText = "<p>" + instanceName + ", " + instanceType + "</p>You can define any number of <b>" + instanceName + "'s</b>, a <b>" + instanceType + " activity</b>. " +
                    "You may also assign each instance with a <b>cost</b> and a <b>reward</b>."
                $('#add-row').text('Add activity instance')
                // tabledata = this.$store.state.activityInstances.filter(x => x.label == instanceName)[0].instanceTableData;
                tabledata = this.$store.state.dm3kGraph.activityInstances.filter(x => x.label == instanceName)[0].instanceTableData;
                tablecols = [{
                        title: "",
                        formatter: "buttonCross",
                        width: 5,
                        hozAlign: "center",
                        cellClick: function(e, cell) {
                            let label = cell.getRow().getData().name
                            removeRow(label)
                        }
                    },
                    {
                        title: instanceName + " instance name",
                        field: "name",
                        editor: "input"
                    },
                ]
                for (let c of costName) {
                    tablecols.push({
                        title: "Cost (" + c + ")",
                        field: "cost_" + c,
                        hozAlign: "left",
                        sorter: "number",
                        editor: "input"
                    })
                }
                if (rewardName != '') {
                    tablecols.push({
                        title: "Reward (" + rewardName + ")",
                        field: "reward",
                        hozAlign: "left",
                        sorter: "number",
                        editor: "input"
                    })
                }
            }
            if (resOrAct == 'Resource' || resOrAct == 'resource') {
                //Columns are Instance | Cost
                titleText = "<p>" + instanceName + ", " + instanceType + "</p>You can define any number of <b>" + instanceName + "'s</b>, a <b>" + instanceType + " resource</b>. You may also assign each instance with a <b>budget</b> amount."
                $('#add-row').text('Add resource instance')
                // Get tabledata for this resource from the graph
                tabledata = this.$store.state.dm3kGraph.resourceInstances.filter(x => x.label == instanceName)[0].instanceTableData;
                tablecols = [{
                        title: "",
                        formatter: "buttonCross",
                        width: 5,
                        hozAlign: "center",
                        cellClick: function(e, cell) {
                            let label = cell.getRow().getData().name
                            removeRow(label)
                        }
                    },
                    {
                        title: instanceName + " instance name",
                        field: "name",
                        editor: "input"
                    }
                ]
                for (let b of budgetName) {
                    tablecols.push({
                        title: "Budget (" + b + ")",
                        field: "budget_" + b,
                        hozAlign: "left",
                        sorter: "number",
                        editor: "input"
                    })
                }
            }
            new Tabulator(this.$refs.table, {
                height: this.TABLEHEIGHT,
                addRowPos: "bottom",
                reactiveData: true,
                data: tabledata,
                layout: this.TABLELAYOUT,
                columns: tablecols,
            });
            $('#table-title').html(titleText)
        },
        showAllocationModal(instanceType, instanceName, resOrAct, budgetName, rewardName, costName, resourceName, activityName) {

            function removeRow(dataObj) {
                let ind = tabledata.findIndex(x => ((x.activityInstance == dataObj.activityInstance) && (x.resourceInstance == dataObj.resourceInstance)))
                tabledata.splice(ind, 1)
            }

            let titleText = ''
            let tablecols = [];
            let tabledata = [];

            this.resourceName = resourceName
            this.activityName = activityName
            $('#alloc-selector').show()
            $('#add-row').text('Add allocation between instances')
            let modal = document.querySelector(".modal")
            modal.style.display = "block"
            modal.style.display = "block"

            //Columns are Instances of resources | Dropdowns for all available instances of activities
            titleText = "Allocated individual resource instances of <b> " + resourceName + " </b>to activity instances of <b>" + activityName + "</b>."
            let resource_instances = this.$store.state.dm3kGraph.resourceInstances.filter(x => x.label == resourceName)[0].instanceTableData.map(x => x.name)
            let activity_instances = this.$store.state.dm3kGraph.activityInstances.filter(x => x.label == activityName)[0].instanceTableData.map(x => x.name)
            resource_instances.push('ALL')
            activity_instances.push('ALL')

            tabledata = this.$store.state.dm3kGraph.allocatedToInstances.filter(x => (x.actName == activityName && x.resName == resourceName))[0].instanceTableData;

            tablecols = [{
                    title: "",
                    formatter: "buttonCross",
                    width: 5,
                    hozAlign: "center",
                    cellClick: function(e, cell) {
                        removeRow(cell.getRow().getData())
                    }
                },
                {
                    title: "resource type: " + resourceName,
                    field: "resourceInstance",
                    width: 200,
                    editor: "select",
                    editorParams: {
                        values: resource_instances,
                        defaultValue: "ALL", //set the value that should be selected by default if the cells value is undefined
                        verticalNavigation: "hybrid"
                    }
                },
                {
                    title: "activity type: " + activityName,
                    field: "activityInstance",
                    width: 200,
                    hozAlign: "left",
                    editor: "select",
                    editorParams: {
                        values: activity_instances,
                        defaultValue: "ALL", //set the value that should be selected by default if the cells value is undefined
                        verticalNavigation: "hybrid"
                    },
                }
            ]
            new Tabulator(this.$refs.table, {
                height: this.TABLEHEIGHT,
                addRowPos: "bottom",
                reactiveData: true,
                data: tabledata,
                layout: this.TABLELAYOUT,
                columns: tablecols,
            });
            $('#table-title').html(titleText)
        },
        showContainsModal(instanceType, instanceName, resOrAct, budgetName, rewardName, costName, parentName, childName) {
            function removeRow(label) {
                let ind = tabledata.findIndex(x => x.name == label)
                tabledata.splice(ind, 1)
            }

            //get data table for the selected res or act type
            $('#add-row').text('Specify contains between instances')
            let modal = document.querySelector(".modal")
            $('#alloc-selector').hide()
            modal.style.display = "block"
            modal.style.display = "block"
            let titleText = ''
            let parent_tabledata = []
            let child_instances = []
            this.parentName = parentName
            this.childName = childName
            //Columns are Instances of Dropdowns for all available instances | Dropdowns for all available instances
            titleText = "Contains relationship between instances of <b> " + parentName + " </b>and<b> " + childName + "</b>."

            let parent_is_resource = this.$store.state.dm3kGraph.resourceInstances.filter(x => x.label == parentName)[0] != undefined
            let parent_is_activity = this.$store.state.dm3kGraph.activityInstances.filter(x => x.label == parentName)[0] != undefined
            let child_is_resource = this.$store.state.dm3kGraph.resourceInstances.filter(x => x.label == childName)[0] != undefined
            let child_is_activity = this.$store.state.dm3kGraph.activityInstances.filter(x => x.label == childName)[0] != undefined

            if (parent_is_resource && child_is_resource) {
                child_instances = this.$store.state.dm3kGraph.resourceInstances.filter(x => x.label == childName)[0].instanceTableData.map(x => x.name)
                parent_tabledata = this.$store.state.dm3kGraph.resourceInstances.filter(x => x.label == parentName)[0].instanceTableData;
            }
            if (parent_is_activity && child_is_activity) {
                child_instances = this.$store.state.dm3kGraph.activityInstances.filter(x => x.label == childName)[0].instanceTableData.map(x => x.name)
                parent_tabledata = this.$store.state.dm3kGraph.activityInstances.filter(x => x.label == parentName)[0].instanceTableData;
            }

            let parent_instances = parent_tabledata.map(x => x.name)
            parent_instances.push('ALL')
            child_instances.push('ALL')

            let containsInstance = this.$store.state.dm3kGraph.getContainsInstance(parentName, childName)
            let tabledata = containsInstance.instanceTableData;

            let tablecols = [{
                    title: "",
                    formatter: "buttonCross",
                    width: 5,
                    hozAlign: "center",
                    cellClick: function(e, cell) {
                        removeRow(cell.getRow().getData())
                    }
                },
                {
                    title: "parent instance",
                    field: "parentInstance",
                    width: 200,
                    editor: "select",
                    editorParams: {
                        values: parent_instances,
                        defaultValue: "ALL", //set the value that should be selected by default if the cells value is undefined
                        verticalNavigation: "hybrid"
                    }
                },
                {
                    title: "child instance",
                    field: "childInstance",
                    width: 200,
                    editor: "select",
                    editorParams: {
                        values: child_instances,
                        defaultValue: "ALL", //set the value that should be selected by default if the cells value is undefined
                        verticalNavigation: "hybrid"
                    }
                }
            ]
            new Tabulator(this.$refs.table, {
                height: this.TABLEHEIGHT,
                addRowPos: "bottom",
                reactiveData: true,
                data: tabledata,
                layout: this.TABLELAYOUT,
                columns: tablecols,
            });
            $('#table-title').html(titleText)
        },
        showSolutionModal(data, problemData) {
            let modal = document.querySelector(".soln-modal")
            $('#alloc-selector').hide()
            modal.style.display = "block"
            modal.style.display = "block"
            var solnMatrixObj = {
                data: data, 
                problemData: problemData,
                width: $('#widthFunctionToggle').val()
            }
            this.solnVis.generateSolnMatrix(solnMatrixObj)
            this.solnVis.generateSolnMatrix(solnMatrixObj) //don't remember why I was calling this twice

            $("#widthFunctionToggle").on('change', () => {
                solnMatrixObj = {
                    data: data, 
                    problemData: problemData,
                    width: $('#widthFunctionToggle').val()
                }
                this.solnVis.generateSolnMatrix(solnMatrixObj)
            })
        }

    }
}
</script>

<style scoped>
    .instance-table{
        height: 30vh !important;
        overflow: scroll;
    }
</style>