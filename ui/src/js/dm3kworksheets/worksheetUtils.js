/** 
*/

// TODO - Needs documentation

/**
 * Fill up the options of the drop down control 'jQuerySelector' using 1 or more dm3kgraph block types
 * 
 * @param {Dm3kGraph} graph: an instance of the Dm3kGraph class
 * @param {array} typeList: an array of string names of types in the Dm3kGraph (e.g. ['resource', 'activity']) 
 * @param {jQueryObject} jQuerySelector: a jQuery object that refers to a drop down control (e.g. $('#startName1'))
 * @param {array} excludeNamesList: an array of strings to not include in the options for the drop down
 */

function worksheetUtil_hideShowWorksheet(){
    $('#menu').toggleClass('shrink')
    if( $('#menu').hasClass('shrink') ){
        $('#hide-worksheet-button').html('Expand worksheet')
    } else{
        $('#hide-worksheet-button').html('Hide worksheet')
    }
}
function worksheetUtil_updateDropDown(graph, typeList, jQuerySelector, excludeNamesList) {
    jQuerySelector.empty();
    let updatedOptions = []
    typeList.forEach(function(typeName, index) {
        //console.log('Looking for: '+typeName)
        let options = graph.getAllNamesOfType(typeName);
        //console.log('Options: ', options)
        updatedOptions = updatedOptions.concat(options);
    });
    
    excludeNamesList.forEach(function(excludeName, index) {
        const i = updatedOptions.indexOf(excludeName);
        if (i > -1) {
            updatedOptions.splice(i, 1);
        }
    });

    //console.log('updatedOptions',updatedOptions)
    return updatedOptions.forEach(x => jQuerySelector.append('<option value="'+x+'">'+x+'</option>'))
}

/**
 * Fill up the options of the drop down control 'jQSelectorChild'  using the parent control 'JQSelectorParent'
 * 
 * @param {Dm3kGraph} graph: an instance of the Dm3kGraph class
 * @param {jQueryObject} jQSelectorChild: a jQuery object that refers to a drop down control (e.g. $('#endName1'))
 * @param {jQueryObject} jQSelectorParent: a jQuery object that refers to a drop down control (e.g. $('#startName1'))
 * @param {array} excludeNamesList: an array of strings to not include in the options for the drop down
 */
function worksheetUtil_updateContainsDropDown(graph, jQSelectorChild, jQSelectorParent, excludeNamesList) {
    //console.log('worksheetUtil_updateContainsDropDown on '+jQSelectorChild.attr('id'));
    jQSelectorChild.empty();
    let parentName = jQSelectorParent.children("option:selected").val();
    //console.log('Looking for options based on parent name: '+parentName);
    let updatedOptions = []
    
    //  resources can only contain resources, and activities can only contain activities
    if (graph.isResource(parentName)) {
        updatedOptions = graph.getAllNamesOfType('resource');
    } else {
        updatedOptions = graph.getAllNamesOfType('activity');
    }
    
    // get rid of the parentName...a parent cannot contain itself
    const parentIndex = updatedOptions.indexOf(parentName);
    if (parentIndex > -1) {
        updatedOptions.splice(parentIndex, 1);
    }

    // get rid of the rest of the exclude list
    //console.log('Options: ', updatedOptions)
    excludeNamesList.forEach(function(excludeName, index) {
        const i = updatedOptions.indexOf(excludeName);
        if (i > -1) {
            updatedOptions.splice(i, 1);
        }
    });

    return updatedOptions.forEach(x => jQSelectorChild.append('<option value="'+x+'">'+x+'</option>'))
}

/**
 * Fill up the options of the drop down control 'jQSelectorTarget'  using the resource control 'JQSelectorSource'
 * 
 * @param {Dm3kGraph} graph: an instance of the Dm3kGraph class
 * @param {jQueryObject} jQSelectorTarget: a jQuery object that refers to a drop down control (e.g. $('#endName1'))
 * @param {jQueryObject} jQSelectorSource: a jQuery object that refers to a drop down control (e.g. $('#startName1'))
 * @param {array} excludeNamesList: an array of strings to not include in the options for the drop down
 */
function worksheetUtil_updateAllocatedDropDown(graph, jQSelectorTarget, jQSelectorSource, excludeNamesList) {
    // console.log('worksheetUtil_updateAllocatedDropDown on '+jQSelectorTarget.attr('id'));
    jQSelectorTarget.empty();
    let resName = jQSelectorSource.children("option:selected").val();
    // console.log('Looking for options based on resource name: '+resName);
    
    // want to look for allocations available to the resName
    let updatedOptions = graph.getAllNamesOfAllocatedFrom(resName);

    // get rid of the exclude list
    //console.log('Options: ', updatedOptions)
    excludeNamesList.forEach(function(excludeName, index) {
        const i = updatedOptions.indexOf(excludeName);
        if (i > -1) {
            updatedOptions.splice(i, 1);
        }
    });

    //console.log('updatedOptions',updatedOptions)
    return updatedOptions.forEach(x => jQSelectorTarget.append('<option value="'+x+'">'+x+'</option>'))
}
function worksheetUtil_populateExistingActivitiesFromGraph(graph){
    $('#actTypeExisting').empty()
    $('#actTypeExisting').append('<option selected style="font-weight: bold;" val="an existing activity">an existing activity</option>')
    $.each(graph.getAllNamesOfType('activity'), function (i, item) {
        $('#actTypeExisting').append($('<option>', {
            value: item,
            text : item
        }));
    });
}
function worksheetUtils_newActivityActivated(){
    if ($('#actType').val() != 'a new activity'){
        $('#actTypeExisting').val('an existing activity')
        $('#actName').removeAttr('disabled');
        $('#rewardName').removeAttr('disabled');
    }
}
function worksheetUtils_existingActivityActivated(){
    if ($('#actTypeExisting').val() != 'an existing activity'){
        $('#actType').val('a new activity')
        $('#actName').attr('disabled', 'disabled');
        $('#rewardName').attr('disabled', 'disabled');
        $("#activity-label").html("Label the instance of the ");
		$("#activity-reward-label").html("The instance has a reward of ");
    }else{
        $('#actName').removeAttr('disabled');
        $('#rewardName').removeAttr('disabled');
    }
}
