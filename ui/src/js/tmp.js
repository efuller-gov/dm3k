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
        let graph = this.dm3kgraph;
    
        if (cellType.includes('AllocatedTo')){
            resOrAct = 'allocation'
            let resourceName = cellName.split('_')[0]
            let activityName = cellName.split('_')[1]
            this.showAllocationModal(instanceType, instanceName, resOrAct, budgetName, rewardName, costName, graph, resourceName, activityName)
        } else if (cellType.includes('Contains')) {
            resOrAct = 'contains'
            let parentName = cellName.split('_')[0]
            let childName = cellName.split('_')[1]
            
            this.showContainsModal(instanceType, instanceName, resOrAct, budgetName, rewardName, costName, graph, parentName, childName)
        } else{
            showModal(instanceType, instanceName, resOrAct, budgetName, rewardName, costName, graph, eventDetail)
        }
    }
}


function showModal(instanceType, instanceName, resOrAct, budgetName, rewardName, costName, graph, details){
    //get data table for the selected res or act type
    let modal = document.querySelector(".modal")
    $('#alloc-selector').hide()
    modal.style.display = "block"
      modal.style.display = "block"
    titleText = ''

    modalInstanceName = instanceName

      if (resOrAct == 'Activity' || resOrAct == 'activity'){
          //Columns are Instance | Reward | Cost
          titleText = "<p>"+instanceName + ", " + instanceType+"</p>You can define any number of <b>" + instanceName + "'s</b>, a <b>"+instanceType+" activity</b>. " +
          "You may also assign each instance with a <b>cost</b> and a <b>reward</b>."
        $('#add-row').text('Add activity instance')
        tabledata = graph.activityInstances.filter(x => x.label == instanceName)[0].instanceTableData;
        tablecols = [
                {title: "", formatter:minusButton, width:5, hozAlign:"center", cellClick:
                    function(e, cell){
                      let label = cell.getRow().getData().name
                      removeRow(label)}
                },
                {title: instanceName+" instance name", field:"name", editor:"input"},
                // {title:"Reward ("+rewardName+")", field:"reward", hozAlign:"left", sorter:"number", editor:"input"},
                // {title:"Cost ("+costName+")", field:"cost", width:100, hozAlign:"left", sorter:"number", editor:"input"},
            ]
        // for (let r of rewardName) {
        // 	tablecols.push({title:"Reward ("+r+")", field:"reward", width:80, hozAlign:"left", sorter:"number", editor:"input"})
        // } //BROKEN for some reason, duplicate rewards get assigned
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
        tabledata = graph.resourceInstances.filter(x => x.label == instanceName)[0].instanceTableData;
        // console.log("Table Data: %O", tabledata)
        tablecols = [
                {title: "", formatter:minusButton, width:5, hozAlign:"center", cellClick:
                    function(e, cell){
                      let label = cell.getRow().getData().name
                      removeRow(label)}
                },
                {title: instanceName + " instance name", field:"name", editor:"input"}]
        for (let b of budgetName) {
            tablecols.push({title:"Budget ("+b+")", field:"budget_"+b, hozAlign:"left", sorter:"number", editor:"input"})
        }
            
    }
    
    // Make it easier to add activities and resources
    modalTableName = instanceName+"_"+resOrAct+"_instance";
    let lastEntryArray = tabledata[tabledata.length-1].name.split("_");
    modalTableNameCnt = parseInt(lastEntryArray[lastEntryArray.length - 1]);

      table = new Tabulator("#modal-instance-table", {
            height:TABLEHEIGHT,
            addRowPos:"bottom",
            reactiveData: true,
            data: tabledata,
            layout:TABLELAYOUT,
            columns:tablecols,
    });
      $('#table-title').html(titleText)
      return table
}
function closeModal(){
    let modal = document.querySelector(".modal")
    modal.style.display = "none"
}
function closeSolnModal(){
    let modal = document.querySelector(".soln-modal")
    modal.style.display = "none"
    worksheetUtil_hideShowWorksheet()
}

function showContainsModal(instanceType, instanceName, resOrAct, budgetName, rewardName, costName, graph, parentName, childName){
    //get data table for the selected res or act type
    $('#add-row').text('Specify contains between instances')
    let modal = document.querySelector(".modal")
    $('#alloc-selector').hide()
    modal.style.display = "block"
      modal.style.display = "block"
      titleText = ''
    //Columns are Instances of Dropdowns for all available instances | Dropdowns for all available instances
    titleText = "Contains relationship between instances of <b> " + parentName + " </b>and<b> " +  childName + "</b>."

    let parent_is_resource = graph.resourceInstances.filter(x => x.label == parentName)[0] != undefined
    let parent_is_activity = graph.activityInstances.filter(x => x.label == parentName)[0] != undefined
    let child_is_resource = graph.resourceInstances.filter(x => x.label == childName)[0] != undefined
    let child_is_activity = graph.activityInstances.filter(x => x.label == childName)[0] != undefined

    if (parent_is_resource && child_is_resource){
        var child_instances = graph.resourceInstances.filter(x => x.label == childName)[0].instanceTableData.map(x => x.name)
        var parent_tabledata = graph.resourceInstances.filter(x => x.label == parentName)[0].instanceTableData;
    }
    if (parent_is_activity && child_is_activity){
        var child_instances = graph.activityInstances.filter(x => x.label == childName)[0].instanceTableData.map(x => x.name)
        var parent_tabledata = graph.activityInstances.filter(x => x.label == parentName)[0].instanceTableData;
    }

    let parent_instances = parent_tabledata.map(x => x.name)
    parent_instances.push('ALL')
    child_instances.push('ALL')
                
    let containsInstance = graph.getContainsInstance(parentName, childName)
    tabledata = containsInstance.instanceTableData;

    tablecols = [
            {title: "", formatter:minusButton, width:5, hozAlign:"center", cellClick:
                function(e, cell){
                  let label = cell.getRow().getData().name
                  removeRow(label)}
            },
            {title: "parent instance", field:"parentInstance", width:200, editor:"select",
                editorParams: {
                    values: parent_instances,
                    defaultValue:"ALL", //set the value that should be selected by default if the cells value is undefined
                    verticalNavigation:"hybrid"}},
            {title: "child instance", field:"childInstance", width:200, editor:"select",
                editorParams: {
                    values: child_instances,
                    defaultValue:"ALL", //set the value that should be selected by default if the cells value is undefined
                    verticalNavigation:"hybrid"}}
        ]
      table = new Tabulator("#modal-instance-table", {
            height:TABLEHEIGHT,
            addRowPos:"bottom",
            reactiveData: true,
            data: tabledata,
            layout:TABLELAYOUT,
            columns:tablecols,
    });
      $('#table-title').html(titleText)
      return table
}

function showAllocationModal(instanceType, instanceName, resOrAct, budgetName, rewardName, costName, graph, resourceName, activityName){
    //get data table for the selected res or act type
    $('#alloc-selector').show()
    $('#add-row').text('Add allocation between instances')
    let modal = document.querySelector(".modal")
    modal.style.display = "block"
      modal.style.display = "block"

      titleText = ''
    //Columns are Instances of resources | Dropdowns for all available instances of activities
    titleText = "Allocated individual resource instances of <b> " + resourceName + " </b>to activity instances of <b>" + activityName + "</b>."
    let res_tabledata = graph.resourceInstances.filter(x => x.label == resourceName)[0].instanceTableData;
    let act_tabledata = graph.activityInstances.filter(x => x.label == activityName)[0].instanceTableData;
    let resource_instances = res_tabledata.map(x => x.name)
    let activity_instances = act_tabledata.map(x => x.name)
    resource_instances.push('ALL')
    activity_instances.push('ALL')
    
    //tabledata = res_tabledata;
    tabledata = graph.getAllocatedToInstance(resourceName, activityName).instanceTableData;

    tablecols = [
            {title: "", formatter:minusButton, width:5, hozAlign:"center", cellClick:
                function(e, cell){
                  let label = cell.getRow().getData().name
                  removeRow(label)}
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
      table = new Tabulator("#modal-instance-table", {
            height:TABLEHEIGHT,
            addRowPos:"bottom",
            reactiveData: true,
            data: tabledata,
            layout:TABLELAYOUT,
            columns:tablecols,
    });
      $('#table-title').html(titleText)
      return table
}
function showSolutionModal(data, problemData){
    let modal = document.querySelector(".soln-modal")
    $('#alloc-selector').hide()
    modal.style.display = "block"
      modal.style.display = "block"
    worksheetUtil_hideShowWorksheet();

    generateSolnMatrix(data, problemData, $('#widthFunctionToggle').val())
    generateSolnMatrix(data, problemData, $('#widthFunctionToggle').val())

    $("#widthFunctionToggle").change(
        function(){
            generateSolnMatrix(data, problemData, $('#widthFunctionToggle').val())
        }
    )
}

