<template>
    <div id="bottom-container">
        <div id="menu">
            <div id="worksheet_menu_column">
                <div id='zoom-buttons'>
					<button @click="zoomIn" id="zoomIn" class='zoom-button'>+</button>
					<button @click="zoomOut" id="zoomOut" class='zoom-button'>-</button>
					<!-- <b class="title-text">Version name</b> -->
				</div>
                <button @click="createResourceTab()" id="create-resources-button" type="button" class="menu-button enabled">Create resources</button>
                <button @click="allocateResourcesTab()" id="allocate-resources-button" type="button" class="menu-button disabled">Allocate resources to activities</button>
                <button @click="containsTab()" id="contains-button" type="button" class="menu-button disabled">Make contains relationship</button>
                <button @click="constrainAllocationsTab()" id="constrain-allocations-button" type="button" class="menu-button disabled">Constrain allocations</button>
            </div>
            <div id="create-resource-column" class="left_column responsive-column-text">
                <p class="title-text"><b>Create a resource.</b></p>
                <label for="resType">My <b>resource</b> is what I am limited by. <br>It can be best described by</label>
                <select class="chosen-select" id="resType">
                    <option value="none">     </option>
                    <!-- <option value="custom input">custom input</option> -->
                </select><br><br>
                <label id="resource-label" for="resName">Label the resource </label>
                <input type="text" id="resName"><br><br>
                <label id ="resource-budget-label" for="budgetName">The resource is budgeted by</label>
                <input type="text" id="budgetName"><br><br>
                <input @click="addResource()" type="button" class="done-button" value="Done" id="addResource">
            </div>
            <div id="allocate-resources-column" class="left_column hide">
                <p><b>Allocate resources to activities.</b></p>
                <span>
                <button @click="newAllocation()" id="new-allocation" type="button" class="menu-button sub-menu activity-choice">New activity <i class="arrow down"></i></button>
                <button @click="existingAllocation()" id="existing-allocation" type="button" class="menu-button sub-menu activity-choice">Existing activity <i class="arrow down"></i></button>
                </span><br>
                <div id="activity-submenu-container" class="hide">
                    <label for="resName2">I want to allocate my</label>
                    <select class="chosen-select" id="resName2">
                        <!--pull from dm3kgraph.resources -->
                    </select>
                    <label for="actType"> to </label>
                    <select @change="worksheetUtils_newActivityActivated" class="chosen-select activity-select" id="actType" style="margin-left: 0px;">
                        <option selected style="font-weight: bold;">a new activity</option>
                        <!-- <option value="custom input">custom input</option> -->
                    </select>
                    <select class="chosen-select activity-select disabled" id="actTypeExisting" onchange="worksheetUtils_existingActivityActivated()">
                        <option style="font-weight: bold;">an existing activity</option>
                    </select>
                </div>
                <br>
                <div id="activity-def-bottom-container" class="hide">
                    <label id="activity-label" for="actName">Label the activity </label>
                    <input type="text" id="actName"><br><br>
                    <label id ="activity-reward-label" for="rewardName">Label the reward of the instance </label>
                    <input type="text" id="rewardName"><br><br>
                </div>
                <div>
                    <input @click="addActivity()" type="button" class="done-button hide" value="Done" id="addActivity">
                </div>
            </div>
            <div id="contains-column" class="left_column hide">
                <p><b>Set up a contains relationship.</b></p>
                <span>
                <button @click="existingContains()" id="existing-contains" type="button" class="menu-button sub-menu activity-choice"> Existing Containers<i class="arrow down"></i></button>
                <button @click="newActContainer()" id="new-activity-contains" type="button" class="menu-button sub-menu activity-choice">New Activity Container <i class="arrow down"></i></button>
                <button @click="newResContainer()" id="new-resource-contains" type="button" class="menu-button sub-menu activity-choice">New Resource Container <i class="arrow down"></i></button>
                </span><br><br>
                <div id="contains-existing-submenu" class="hide">
                    <label for="parentName2">I want </label>
                    <select class="chosen-select" id="parentName2">
                        <!--pull from dm3kgraph.resources or activities -->
                    </select>
                    <label for="childName2"> to contain </label>
                    <select class="chosen-select" id="childName2">
                        <!--pull from dm3kgraph.resources or activities -->
                    </select>
                    <br><br>
                    <input @click="doneWithContains()" type="button" class="done-button" value="Contains Done" id="addContains">
                </div>
                <div id="contains-new-act-submenu" class="hide">
                    <label for="actType2"> I want </label>
                    <select class="chosen-select activity-select" id="actType2" style="margin-left: 0px;" @change="worksheetUtils_newActivityActivated">
                        <option selected style="font-weight: bold;">a new activity</option>
                        <!-- <option value="custom input">custom input</option> -->
                    </select>
                    <label for="act-childName">to contain</label>
                    <select class="chosen-select" id="act-childName">
                        <!--pull from dm3kgraph.resources -->
                    </select>
                    <br><br>
                    <label id="activity-label" for="act-parentName">Label the activity </label>
                    <input type="text" id="act-parentName"><br><br>
                    <label id ="activity-reward-label" for="act-parentRewardName">Label the reward of the instance </label>
                    <input type="text" id="act-parentRewardName"><br><br>
                    <input @click="addNewActContains" type="button" class="done-button" value="Contains Done" id="addNewActContains">
                </div>
                <div id="contains-new-res-submenu" class="hide">
                    <label for="resType2"> I want </label>
                    <select class="chosen-select activity-select" id="resType2" style="margin-left: 0px;" @change="worksheetUtils_newResourceActivated">
                        <option selected style="font-weight: bold;">a new resource</option>
                        <!-- <option value="custom input">custom input</option> -->
                    </select>
                    <label for="res-childName">to contain</label>
                    <select class="chosen-select" id="res-childName">
                        <!--pull from dm3kgraph.resources -->
                    </select>
                    <br><br>
                    <label id="parent-label" for="res-parentName">Label the parent </label>
                    <input type="text" id="res-parentName"><br><br>
                    <input @click="addNewResContains" type="button" class="done-button" value="Contains Done" id="addNewResContains">
                </div>
            </div>
            <div id="make-allocation-constraint-column" class="left_column hide">
                <p><b>Set up an allocation constraint.</b><br><br> I want the allocation</p>
                <label for="startName1">from </label>
                <select class="chosen-select" id="startName1">
                    <!--pull from dm3kgraph.resources -->
                </select>
                <label for="stopName1"> to </label>
                <select class="chosen-select" id="stopName1">
                    <!--pull from dm3kgraph.resources or activities -->
                </select>
                <p> to constrain the allocation </p>
                <label for="startName2">from </label>
                <select class="chosen-select" id="startName2">
                    <!--pull from dm3kgraph.resources -->
                </select>
                <label for="stopName2"> to </label>
                <select class="chosen-select" id="stopName2">
                    <!--pull from dm3kgraph.resources or activities -->
                </select>
                <br><br><label for="constraintType">with constraint type</label>
                <select class="chosen-select" id="constraintType">
                    <option value="none">     </option>
                    <option value="ifThen">Contained IF-THEN</option>
                    <option value="ifNot">IF-NOT</option>
                    <option value="ifOnly">IF-ONLY</option>
                </select>
                <br><br>
                <input @click="addConstraint" type="button" class="done-button" value="Done" id="addConstraint">
            </div>
            <div id="explanatory-info-column" class="persistent_left_column">
				<p id="pane-level-explanatory-title" class="title-text">Pane-level explanatory text</p>
				<p id="pane-level-explanatory-text" class="explanatory-text">Explanatory text here, generated for each tab/ worksheet.</p>
				<p id="instance-level-explanatory-title" class="title-text">Instance-level explanatory text</p>
				<p id="instance-level-explanatory-text">Explanatory text here, generated for each tab/ worksheet.</p>
				<img id="create-resources-helper-image" class="helper-img hide" src="../assets/create-resource.svg">
                <img id="allocate-resources-helper-image" class="helper-img hide" src="../assets/allocate-resources.svg">
                <img id="contains-helper-image" class="helper-img hide" src="../assets/contains-relationship.svg">
                <img id="constrain-allocations-helper-image" class="helper-img hide" src="../assets/allocation-constraint.svg">
				<!-- <img id="helper-image" :src="src[currentSrc]"> -->
                <!-- <img id="helper-image" :src="resolve_img_url(picture_src)" /> -->
				<p id="i-circle-explainer" class="explanatory-text">By clicking <img src="../assets/rounded-info-icon-gray.png" alt="circle-info" style="vertical-align:text-bottom;" height="20" width="auto">
					on any item, see actions that can be taken to define further relationships and instances.</p>
            </div>
            <div id="helper-info-div">
				<button @click="worksheetUtil_hideShowWorksheet()" id="hide-worksheet-button" class='zoom-button'>Hide worksheet</button>
				<p class="title-text"><b>Load, save, and submit diagrams.</b></p>
				<!-- <p>Load diagram from local machine</p> -->
				<input @click.self="getConfigFile" type="button" class="done-button" value="Load existing diagram"><br><br><br>
				<div style='height: 0px;width: 0px;overflow: hidden;'><input type="file" id="loadLocally" accept="application/json"></div>
				<!-- <p>Save diagram to work on later</p> -->
				<label for="diagramName">Save current diagram as </label>
				<input type="text" class="long-input" id="diagramName" value="dm3kDiagram" ><br>
				<input @click="saveLocally" type="button" class="done-button" value="Save file" id="saveLocally" style="margin-top: 10px;"><br><br>
				<p><br>Click below to submit your scenario to DM3K for solving.<br>
					You may return here to edit your scenario afterwards.</p>
				<label for="algType">Algorithm Type</label>
				<select class="chosen-select" id="algType">
					<option value="KnapsackViz">Knapsack</option>
					<option value="FullHouseViz">FullHouse</option>
				</select><br>
                <input @click="submitDM3K()" style="margin-top: 10px;" type="button" class="done-button" value="Submit to DM3K" id="submitDM3K">
            </div>
        </div>  
    </div>
</template>

<script>
import $ from 'jquery'
import {Dm3kConverter} from '../js/dm3kconversion/dm3kconversion';

export default {
    name: 'WorksheetPane',
    methods: {
        zoomIn(){
            this.$root.$emit('zoom-in')            
		},
        zoomOut(){
            this.$root.$emit('zoom-out')            
		},
        populateResourcesFromWB() {
            $.each(this.RESOURCE_WORD_BANK, function (i, item) {
                $('#resType').append($('<option>', {
                    value: item,
                    text : item
                }));
                $('#resType2').append($('<option>', {
                    value: item,
                    text : item
                    }));
                });
        },
        populateActivitiesFromWB() {
            $.each(this.ACTIVITY_WORD_BANK, function (i, item) {
                $('#actType').append($('<option>', {
                    value: item,
                    text : item
                }));
                $('#actType2').append($('<option>', {
                    value: item,
                    text : item
                    }));
                });
        },
        worksheetUtil_hideShowWorksheet(){
            $('#menu').toggleClass('shrink')
            if( $('#menu').hasClass('shrink') ){
                $('#hide-worksheet-button').html('Expand worksheet')
            } else{
                $('#hide-worksheet-button').html('Hide worksheet')
            }
        },
        resetResourcePrompt(){
            $('#resType').val("none")
            $('#resName').val("")
            $('#budgetName').val("")
            $("#resource-label").html("Label the resource ");
            $("#resource-budget-label").html("The resource is budgeted by ");
		},
        resetActivityPrompt(){
			$('#resName2').val("none")
			$('#actType').val("a new activity")
			$('#actTypeExisting').val("an existing activity")
			$('#actName').val("")
			$('#rewardName').val("")
			$('#costName').val("")
			$('#activity-label').html("Label the activity ");
			$('#activity-reward-label').html("Label the reward of the instance ");
			$('#activity-def-bottom-container').addClass('hide')
			$('#activity-submenu-container').addClass('hide')
			$('#actType').addClass('hide')
			// $('#actTypeExisting').addClass('hide')
			$('#addActivity').addClass('hide')
			$('.activity-choice').removeClass('enabled')
        },
        resetContainsPrompt(){
			$('#contains-existing-submenu').addClass('hide')
			$('#contains-new-act-submenu').addClass('hide')
			$('#contains-new-res-submenu').addClass('hide')
        },
        changeHelperText(worksheetName){
            let helperText = this.helper_text.filter(x=>x.worksheet==worksheetName)[0]
            $('#pane-level-explanatory-title').text(helperText['pane-title-text']);
            $('#pane-level-explanatory-text').html(helperText['pane-body-text']);
            $('#instance-level-explanatory-title').hide();
            $('#instance-level-explanatory-text').hide();
        },
        changeHelperImg(worksheetName){
            let worksheet_names = ["allocate-resources", "create-resources", "contains", "constrain-allocations"]
            let helperImg = this.helper_images_info.filter(x=>x.worksheet==worksheetName)[0]
            $('#'+worksheetName+"-helper-image").width(helperImg['scale-width']);
            $('#pane-level-explanatory-text').css('font-size', helperImg['text-size']);
            $(".helper-image").addClass('hide')
            for (let wk of worksheet_names.filter(x=>x!=worksheetName)){
                $('#'+wk+"-helper-image").addClass('hide')
            }
            $('#'+worksheetName+"-helper-image").removeClass('hide')
        },
        createResourceTab(){
            $(".menu-button").removeClass('enabled')
            $(".left_column").addClass('hide')
            $("#create-resource-column").removeClass('hide')
            $("#create-resources-button").addClass('enabled')
            this.changeHelperText('create-resources')
            this.changeHelperImg('create-resources')
			this.resetActivityPrompt()
			this.resetContainsPrompt()
        },
        addResource(){
            
            $('#allocate-resources-button').removeClass('disabled')
            $('#contains-button').removeClass('disabled')

            var newResType = $("#resType").val();
            if ( (newResType=='none') | (newResName=='')){
                alert('Please provide a label to create a new resource.')
                return
            }
            
            var newBudgetName = $("#budgetName").val();
            let budgetNameList = newBudgetName.split(",");
            let newBudgetNameList = budgetNameList.map(s => s.trim())  // trim in case user but in a space with comma
            var newResName = $("#resName").val();

            let model = this.$store.state.dm3kGraph.graph.getModel()
            if (model.getCell(newResName) != undefined){
                alert('Cannot create duplicate node. Please choose a new instance name.')

            } else{
                var ans = this.$store.state.dm3kGraph.addCompleteResource(newResType, newResName, newBudgetNameList);

                if (ans.success) {
                    this.updateAllDropDowns();
                    // var layout = new mxGraphLayout(dm3kgraph.graph);
                    // executeLayout(dm3kgraph.graph, layout);
                    this.resetResourcePrompt();
                }
                else {
                    alert(ans.details);
                }
            }
        },
        allocateResourcesTab(){
            $(".menu-button").removeClass('enabled')
            $(".left_column").addClass('hide')
            $("#allocate-resources-column").removeClass('hide')
            $("#allocate-resources-button").addClass('enabled')
            this.changeHelperText('allocate-resources')
            this.changeHelperImg('allocate-resources')
            this.resetContainsPrompt()
        },
        newAllocation(){
            $('#activity-submenu-container').removeClass('hide')
            $('#activity-def-bottom-container').removeClass('hide')
            $('#existing-allocation').removeClass('enabled')
            $('#new-allocation').addClass('enabled')
            $('#actType').removeClass('hide')
            $('#actTypeExisting').addClass('hide')
            $('#addActivity').removeClass('hide')
        },
        existingAllocation(){
            $('#activity-submenu-container').removeClass('hide')
            $('#activity-def-bottom-container').addClass('hide')
            $('#new-allocation').removeClass('enabled')
            $('#existing-allocation').addClass('enabled')
            $('#actType').addClass('hide')
            $('#actTypeExisting').removeClass('hide')
            $('#addActivity').removeClass('hide')
        },
        addActivity(){
            $('#constrain-allocations-button').removeClass('disabled')
            $('#actTypeExisting').removeClass('disabled')

            var newActType = $("#actType").val();
            var newActName = $("#actName").val();
            var existingResName = $("#resName2").val();
            var newRewardName = $("#rewardName").val();
            if ($('#new-allocation').hasClass('enabled') & ( (newActType=='none') | (newActName=='') ) ){
                alert('Please fill all fields required to create an activity.')
                return
            }
            if( $('#existing-allocation').hasClass('enabled') & $('#actTypeExisting').val() == 'an existing activity'){
                alert('You must select an existing activity from the dropdown menu.')
                return
            }
            if( $('#new-allocation').hasClass('enabled') & $('#actType').val() == 'a new activity'){
                alert('You must select a new activity type from the dropdown menu.')
                return
            }
            // let model = this.$store.state.dm3kGraph.graph.getModel()
            // If user tries to add both a new and existing activity. This shouldn't happen, but just in case...
            // if ($("#actType").val() != 'a new activity' && $("#actTypeExisting").val() != 'an existing activity') {
            //     // resetActivityPrompt();
            //     alert('Choose either a new activity or an existing activity to allocate to. Do not select both.')
            // }

            // Allocate to existing activity
            if ($("#actType").val() == 'a new activity'){
                let actName = $("#actTypeExisting").val();
                let actCell = this.$store.state.dm3kGraph.getActivity(actName)
                let actType = actCell.getId()
                let duplicateAlloc = 0
                // check if allocation b/w this res and act already exists
                this.$store.state.dm3kGraph.allocatedLinks.forEach(function(link){
                    if (link.source.getValue()==existingResName & link.target.getValue()==actName){
                        alert('Allocation between '+existingResName+' and '+actName+' already exists.')
                        duplicateAlloc = 1
                    }
                })
                if (duplicateAlloc) {
                    return
                }
                let costNum = Object.keys(this.$store.state.dm3kGraph.costs).length
                let  ans = this.$store.state.dm3kGraph.addCompleteActivity(actType, actName, existingResName, newRewardName, costNum);
                if (ans.success) {
                        this.updateAllDropDowns();
                        // var layout = new mxGraphLayout(this.$store.state.dm3kGraph.graph);
                        // executeLayout(this.$store.state.dm3kGraph.graph, layout);
                        // resetActivityPrompt();
                    }
                    else {
                        alert(ans.details);
                    }
            } else{
            // Allocate to new activity, and create new activity
                // if (model.getCell(newActName) != undefined){
                //     alert('Cannot create duplicate node. Please choose a new instance name.')
                // } else{
                    if (newActType.includes('[')){
                        let tmp = newActType.split('[')
                        tmp = newActType.split(']',2)

                        newActType = tmp[0].split('[')[1];
                        newActName = tmp[1]
                    }
                    let costNum = Object.keys(this.$store.state.dm3kGraph.costs).length
                    let ans = this.$store.state.dm3kGraph.addCompleteActivity(newActType, newActName, existingResName, newRewardName, costNum);
                    if (ans.success) {
                        this.updateAllDropDowns();
                        // var layout = new mxGraphLayout(dm3kgraph.graph);
                        // executeLayout(dm3kgraph.graph, layout);
                        // resetActivityPrompt();
                    }
                    else {
                        alert(ans.details);
                    }
                // }
            }
        },
        containsTab(){
            $(".menu-button").removeClass('enabled')
            $(".left_column").addClass('hide')
            $("#contains-column").removeClass('hide')
            $("#contains-button").addClass('enabled')
            this.changeHelperText('contains')
            this.changeHelperImg('contains')
            this.resetActivityPrompt()
        },
        constrainAllocationsTab(){
            $(".menu-button").removeClass('enabled')
            $(".left_column").addClass('hide')
            $("#make-allocation-constraint-column").removeClass('hide')
			$("#constrain-allocations-button").addClass('enabled')
            this.changeHelperImg('constrain-allocations')
            this.changeHelperText('constrain-allocations')
			this.resetActivityPrompt()
            this.resetContainsPrompt()
            this.updateAllDropDowns()
        },
        existingContains(){
            $('#contains-existing-submenu').removeClass('hide')
			$('#contains-new-act-submenu').addClass('hide')
			$('#contains-new-res-submenu').addClass('hide')
        },
        newActContainer(){
            $('#contains-existing-submenu').addClass('hide')
			$('#contains-new-act-submenu').removeClass('hide')
			$('#contains-new-res-submenu').addClass('hide')
        },
        newResContainer(){
            $('#contains-existing-submenu').addClass('hide')
			$('#contains-new-act-submenu').addClass('hide')
			$('#contains-new-res-submenu').removeClass('hide')
        },
        addNewResContains(){
            var parent = $('#res-parentName').val();
            var child = $('#res-childName').val();
            var parentType = $('#resType2').val();
             this.$store.state.dm3kGraph.addNewResContains(parentType, parent, child);
            this.updateAllDropDowns();
        },
        addNewActContains(){
            var parent = $('#act-parentName').val();
            var child = $('#act-childName').val();
            var reward = $('#act-parentRewardName').val();
            var parentType = $('#actType2').val();
            this.$store.state.dm3kGraph.addNewActContains(parentType, parent, child, reward);
            this.updateAllDropDowns();
        },
        doneWithContains(){
            let parent = $('#parentName2').val();
            let child = $('#childName2').val();
            let parent_is_resource = this.$store.state.dm3kGraph.resourceInstances.filter(x => x.label == parent)[0] != undefined
            let parent_is_activity = this.$store.state.dm3kGraph.activityInstances.filter(x => x.label == parent)[0] != undefined
            let child_is_resource = this.$store.state.dm3kGraph.resourceInstances.filter(x => x.label == child)[0] != undefined
            let child_is_activity = this.$store.state.dm3kGraph.activityInstances.filter(x => x.label == child)[0] != undefined
            if ( (parent_is_resource && child_is_activity) || (parent_is_activity && child_is_resource) ){
                alert('You are trying to contain a resource with an activity or an activity with a resource. ' +
                    '\n\nContains relationships can only be created between resource and resource or activity and activity.')
                return
            }
            this.$store.state.dm3kGraph.addContains(parent, child)
        },
        addConstraint(){
            let fromName1 = $("#startName1").val();
            let toName1 = $("#stopName1").val();
            let fromName2 = $("#startName2").val();
            let toName2 = $("#stopName2").val();
            let constraintType = $("#constraintType").find(":selected").text()

            this.$store.state.dm3kGraph.addConstraint(fromName1, toName1, fromName2, toName2, constraintType);
        },
        worksheetUtil_updateContainsDropDown(graph, jQSelectorChild, jQSelectorParent, excludeNamesList) {
            console.log('worksheetUtil_updateContainsDropDown on '+jQSelectorChild.attr('id'));
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
            excludeNamesList.forEach(function(excludeName) {
                const i = updatedOptions.indexOf(excludeName);
                if (i > -1) {
                    updatedOptions.splice(i, 1);
                }
            });

            return updatedOptions.forEach(x => jQSelectorChild.append('<option value="'+x+'">'+x+'</option>'))
        },
        updateAllDropDowns() {
			// update the "Allocate resources to activities" worksheet
			this.worksheetUtil_updateDropDown(this.$store.state.dm3kGraph, ['resource'], $('#resName2'),[]);

			// update the "Make contains relationship" worksheet
            this.worksheetUtil_updateDropDown(this.$store.state.dm3kGraph, ['resource', 'activity'], $('#parentName2'), []);
            this.worksheetUtil_updateDropDown(this.$store.state.dm3kGraph, ['resource', 'activity'], $('#childName2'), []);
			// this.worksheetUtil_updateContainsDropDown(this.$store.state.dm3kGraph, $('#childName2'), $('#parentName2'), []);

			this.worksheetUtil_updateDropDown(this.$store.state.dm3kGraph, ['activity'], $('#act-childName'), [])
			this.worksheetUtil_updateDropDown(this.$store.state.dm3kGraph, ['resource'], $('#res-childName'), [])

            // update the "Constrain allocations" worksheet
			this.worksheetUtil_updateDropDown(this.$store.state.dm3kGraph, ['resource'], $('#startName1'), []);
			this.worksheetUtil_updateAllocatedDropDown(this.$store.state.dm3kGraph, $('#stopName1'), $('#startName1'), []);
			this.worksheetUtil_updateDropDown(this.$store.state.dm3kGraph, ['resource'], $('#startName2'), []);
			this.worksheetUtil_updateAllocatedDropDown(this.$store.state.dm3kGraph, $('#stopName2'), $('#startName2'), [$('#stopName1').children("option:selected").val()]);

			// this.worksheetUtil_populateExistingActivitiesFromGraph(g)

        },
        worksheetUtil_updateAllocatedDropDown(graph, jQSelectorTarget, jQSelectorSource, excludeNamesList) {
            // console.log('worksheetUtil_updateAllocatedDropDown on '+jQSelectorTarget.attr('id'));
            jQSelectorTarget.empty();
            let resName = jQSelectorSource.children("option:selected").val();
            // console.log('Looking for options based on resource name: '+resName);
            
            // want to look for allocations available to the resName
            let updatedOptions = graph.getAllNamesOfAllocatedFrom(resName);

            // get rid of the exclude list
            //console.log('Options: ', updatedOptions)
            excludeNamesList.forEach(function(excludeName) {
                const i = updatedOptions.indexOf(excludeName);
                if (i > -1) {
                    updatedOptions.splice(i, 1);
                }
            });

            //console.log('updatedOptions',updatedOptions)
            return updatedOptions.forEach(x => jQSelectorTarget.append('<option value="'+x+'">'+x+'</option>'))
        },
        updateDropDown(resList, jQuerySelector) {
            jQuerySelector.empty();
            return resList.forEach(x => jQuerySelector.append('<option value="'+x+'">'+x+'</option>'))
        },
        worksheetUtil_updateDropDown(graph, typeList, jQuerySelector, excludeNamesList) {
            // console.log('worksheetUtil_updateDropDown on '+jQuerySelector.attr('id'));

            jQuerySelector.empty();
            let updatedOptions = []
            typeList.forEach(function(typeName) {
                //console.log('Looking for: '+typeName)
                let options = graph.getAllNamesOfType(typeName);
                //console.log('Options: ', options)
                updatedOptions = updatedOptions.concat(options);
            });
            
            excludeNamesList.forEach(function(excludeName) {
                const i = updatedOptions.indexOf(excludeName);
                if (i > -1) {
                    updatedOptions.splice(i, 1);
                }
            });

            return updatedOptions.forEach(x => jQuerySelector.append('<option value="'+x+'">'+x+'</option>'))
        },
        worksheetUtils_newActivityActivated(){
            if ($('#actType').val() != 'a new activity'){
                $('#actTypeExisting').val('an existing activity')
                $('#actName').removeAttr('disabled');
                $('#rewardName').removeAttr('disabled');
            }
            this.worksheetUtil_updateDropDown(this.$store.state.dm3kGraph, ['activity'], $('#act-childName'), [])
			// worksheetUtil_updateDropDown(g, ['resource'], $('#res-childName'), [])
        },
        worksheetUtils_newResourceActivated(){
            $('#res-childName').removeAttr('disabled');
            this.worksheetUtil_updateDropDown(this.$store.state.dm3kGraph, ['resource'], $('#res-childName'), [])
        },
        worksheetUtils_existingActivityActivated(){
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
            this.worksheetUtil_updateDropDown(this.$store.state.dm3kGraph, ['activity'], $('#act-childName'), [])
			// worksheetUtil_updateDropDown(g, ['resource'], $('#res-childName'), [])
        },
        resetDropdowns(){
            $('#resName2').empty()
            $('#actName').empty()
            $('#rewardName').empty()
            $('#actTypeExisting').empty()
            $('#parentName2').empty()
            $('#childName2').empty()
            $('#res-ChildName').empty()
            $('#act-ChildName').empty()
        },
        getConfigFile(){
            
            this.$emit('clear-graph')
            this.$root.$emit('clear-graph')
            this.resetDropdowns()
            
            let promise = new Promise(function(resolve) {
                $('#loadLocally').trigger('click')

                // Load a file from local storage
                $("#loadLocally").change(function(e) {
                    const file = e.target.files[0];
                    console.log("--> LOAD LOCALLY ", e)
                    if (!file) {
                        return;
                    }

                    var reader = new FileReader()
                    reader.onload = function(e) {
                        var inputJsonString = e.target.result;
                        
                        var inputJson = JSON.parse(inputJsonString);
                        this.inputJson = inputJson;
                        resolve(inputJson)
                        // dm3kconversion_reverse(dm3kgraph, inputJson);
                        // // update the worksheets and make sure all worksheets are enabled
                        // this.updateAllDropDowns();
                        $('#allocate-resources-button').removeClass('disabled')
                        $('#contains-button').removeClass('disabled')
                        $('#constrain-allocations-button').removeClass('disabled')
                        $('#actTypeExisting').removeClass('disabled')
                    }
                    reader.readAsText(file);
                })
            });

            // resolve runs the first function in .then
            promise.then(
                result => this.readFromJson(result),
                error => alert(error)
            );
        },
        readFromJson(inputJson){
            console.log(" --> inputJson ", inputJson)
            this.dm3kconversion_reverse(this.$store.state.dm3kgraph, inputJson.files[0].fileContents);
        },
        dm3kconversion_reverse(dm3kgraph, inputJson) {
            this.$store.state.dm3kGraph.clearAll();  // this should get rid of all boxes and lines on graph
            console.log("Loading...")
        
            // add resource class boxes to diagram
            for (let rc of inputJson.resourceClasses) {

                // add the resource to the graph
                this.$store.state.dm3kGraph.addCompleteResource(
                    rc.typeName,
                    rc.className,
                    rc.budgets,
                    rc.locX,
                    rc.locY);
            }

            // add activity class boxes and canBeAllocated to links
            // console.log("...activity classes...")
            // console.log(inputJson.activityClasses)
            for (let ac of inputJson.activityClasses) {
                
                let actName = ac.className;
                // console.log(actName)

                // determine which resources are allocated to this activity
                
                let resAllocList = []
                for (let rc of inputJson.resourceClasses) {
                var resName = rc.className;
                for (let cbat of rc.canBeAllocatedToClasses) {
                    if (cbat == actName) {
                    resAllocList.push(resName)
                    }
                }
                }
                // console.log(resAllocList)

                // add the activity and add any allocated to links
                for (let [i, ra] of resAllocList.entries()) {
                
                this.$store.state.dm3kGraph.addCompleteActivity(
                    ac.typeName,
                    ac.className,
                    ra,
                    ac.rewards[0], // TODO - need to make it work for mulitple rewards
                    i,
                    ac.locX,
                    ac.locY,
                )
                }
            }

            // console.log("...contains links - resources....");
            // add contains links - resources
            for (let rc of inputJson.resourceClasses) {
                let resName = rc.className;

                // NOTE - resources should always exist...so no need to do check like contains links - activities below

                for (let ccName of rc.containsClasses) {
                    this.$store.state.dm3kGraph.addContains(resName, ccName);
                }
            }

            // console.log("...contains links - activities...");
            // add contains links - activities
            for (let ac of inputJson.activityClasses) {
                let actName = ac.className;

                // check to see if actName exists, if it doesnt...its a container activity
                let ai_dm3k = this.$store.state.dm3kGraph.getActivityInstance(actName);
                if (ai_dm3k == undefined) {
                this.$store.state.dm3kGraph.addNewActContains(
                    ac.typeName, 
                    actName, 
                    ac.containsClasses[0],  // do the first one this way, then do rest in loop below
                    ac.rewards[0]) // TODO - need to make it work for mulitple rewards)
                for (let ccName of ac.containsClasses.slice(1)) {
                    console.log('Attempting to make a contains link between: '+actName+' and '+ccName);
                    this.$store.state.dm3kGraph.addContains(actName, ccName);
                    console.log(this.$store.state.dm3kGraph.containsLinks)
                }
                }
                // else it is defined and therefore already available to add contains links to
                else {   
                for (let ccName of ac.containsClasses) {
                    console.log('Attempting to make a contains link between: '+actName+' and '+ccName);
                    this.$store.state.dm3kGraph.addContains(actName, ccName);
                    console.log(this.$store.state.dm3kGraph.containsLinks)
                }
                }
                
            }
            
            // console.log("...resource instances...");
            // console.log(inputJson.resourceInstances)

            // Add resource instances
            for (let ri of inputJson.resourceInstances) {
                // console.log(ri)
                let ri_name = ri.className;
                let ri_dm3k = this.$store.state.dm3kGraph.getResourceInstance(ri_name);
                ri_dm3k.clearInstanceTable();
                for (let ri_instance of ri.instanceTable) {
                    ri_dm3k.addToInstanceTable(ri_instance.instanceName, ri_instance.budget);
                }
            }

            // console.log("...activity instances...");
            // console.log(inputJson.activityInstances);
            // Add activity instances
            for (let ai of inputJson.activityInstances) {
                // console.log(ai);
                let ai_name = ai.className;
                // console.log(ai_name);
                // console.log(this.$store.state.dm3kGraph.activityInstances)
                let ai_dm3k = this.$store.state.dm3kGraph.getActivityInstance(ai_name);
                ai_dm3k.clearInstanceTable();
                for (let ai_instance of ai.instanceTable) {
                    ai_dm3k.addToInstanceTable(ai_instance.instanceName, ai_instance.reward, ai_instance.cost);
                }
            }

            // console.log("...allocation instances...")
            // console.log(inputJson.allocationInstances)
            // add allocation instances
            for (let ati of inputJson.allocationInstances) {
                let res_name = ati.resourceClassName;
                let act_name = ati.activityClassName;
                let ati_dm3k = this.$store.state.dm3kGraph.getAllocatedToInstance(res_name, act_name);
                ati_dm3k.clearInstanceTable();
                for (let ati_instance of ati.instanceTable) {
                    ati_dm3k.addToInstanceTable(ati_instance.resourceInstanceName, ati_instance.activityInstanceName);
                }
            }

            // add contains instances
            for (let ci of inputJson.containsInstances) {
                let parent_name = ci.parentClassName;
                let child_name = ci.childClassName;
                let ci_dm3k = this.$store.state.dm3kGraph.getContainsInstance(parent_name, child_name);
                ci_dm3k.clearInstanceTable();
                for (let ci_instance of ci.instanceTable) {
                    ci_dm3k.addToInstanceTable(ci_instance.parentInstanceName, ci_instance.childInstanceName);
                }
            }

            // add allocation contraints
            for (let allc of inputJson.allocationConstraints) {
                let a1FromName = allc.allocationStart.resourceClass;
                let a1ToName = allc.allocationStart.activityClass;
                let a2FromName = allc.allocationEnd.resourceClass;
                let a2ToName = allc.allocationEnd.activityClass;
                let aType = allc.allocationConstraintType;
                this.$store.state.dm3kGraph.addConstraint(a1FromName, a1ToName, a2FromName, a2ToName, aType);
            }
            this.updateAllDropDowns()
        },
        emitSolnModal(e){
            this.worksheetUtil_hideShowWorksheet()
            this.$root.$emit('show-solution-modal', e)
        },
        submitDM3K(){

            console.log("----> ABOUT to submit. Here is graph.  ", this.$store.state.dm3kGraph)
            let outputJson = this.dm3kConverter.dm3kconversion_base(this.$store.state.dm3kGraph);

            // get dataset name from textbox
            var dsName = $("#diagramName").val();

            let alg = $("#algType option:selected").val();

            console.log("Algorithm: "+alg);

            var data_to_send = {
                    "datasetName": dsName,
                    "algorithm": alg,
                        "files": [
                        {
                            "fileName": "dm3k-viz.json",
                            "fileContents": outputJson
                        }
                    ]
            }
            var json_body = JSON.stringify(data_to_send);
            var body = []

            // make a file in Dm3K backend and solve it
            var post_request = $.ajax({
                type: "POST",
                url: "/api/vizdata",
                contentType: "application/json; charset=utf-8",
                data: json_body
            });

            post_request.done((msg) => {
                var jsonMsg = msg;  // its already an object...no need for $.parseJSON(msg)
                let statusCode = jsonMsg["statusCode"];
                if (statusCode != 200) {
                    alert("Failed Attempt to Submit to DM3K: " +
                            jsonMsg + "\n" +
                            jsonMsg["body"] /*+ "\n" +
                            body["internal_message"]*/ );
                    body = $.parseJSON(jsonMsg["body"]);
                }
                else {
                    body = jsonMsg["body"] 
                    this.emitSolnModal({body: body, outputJson: outputJson})
                }
            })
            
            console.log({body: body, outputJson: outputJson})
            console.log("JSON OUTPUT ", JSON.stringify(outputJson))

            post_request.fail(function(jqXHR, textStatus, errorThrown) {
                console.log("Request to vizdata failed: "+textStatus);
                console.log(errorThrown)
                alert("Failed Attempt to Submit to DM3K");
            });
        },
        saveLocally(){
            console.log("Saving a file to local...")
            // capture all of graph in outputjson
            let outputJson = this.dm3kConverter.dm3kconversion_base(this.$store.state.dm3kGraph);
            let outputJsonString = JSON.stringify(outputJson,null,4);
            console.log(outputJsonString);

            // get dataset name from textbox
            let dsName = $("#diagramName").val();
            
            // Taken from https://stackoverflow.com/questions/11071473/how-can-javascript-save-to-a-local-file
            let bb = new Blob([outputJsonString], {type: 'text/plain'});
            let a = document.createElement('a');
            a.download = dsName+'.json';
            a.href = window.URL.createObjectURL(bb);
            a.click();
		}
    },
    data() {
        return{
            RESOURCE_WORD_BANK : [
                "labor",
                "capital",
                "material",
                "facility",
                "time",
                "container",
                "computer",
                "equipment",
                "supplies",
                "weapon"],
            ACTIVITY_WORD_BANK : [
                "assignment",
                "product",
                "item",
                "area",
                "role",
                "action",
                "project",
                "job",
                "target"],
            dm3kConverter: {},
            inputJson: [],
            helper_images_info: [
                {
                    'worksheet': 'create-resources',
                    'img-path': '../assets/create-resource.svg',
                    'text-size': '12px',
                    'scale-width': '95%'
                },
                {
                    'worksheet': 'allocate-resources',
                    'img-path': '../assets/allocate-resources.svg',
                    'text-size': '12px',
                    'scale-width': '95%'
                },
                {
                    'worksheet': 'contains',
                    'img-path': '../assets/contains-relationship.svg',
                    'text-size': '12px',
                    'scale-width': '75%'
                },
                {
                    'worksheet': 'constrain-allocations',
                    'img-path': '../assets/allocation-constraint.svg',
                    'text-size': '11px',
                    'scale-width': '92%'
                }],
            helper_text : [
                {
                    'worksheet': 'create-resources',
                    'pane-title-text': 'Begin building your decision scenario by creating resources.',
                    'pane-body-text': '<b>Resources</b> are entities that get allocated. In the example below, our <b>resource</b> is a <b>backpack</b>. ' +
                                    'We have a finite number of backpacks to fill, so we frame our allocation problem around them. ' +
                                    'Notice that ' +
                                    'each backpack is budgeted by something. Our <b>budget</b> is how we measure the use of a resource. For a backpack, we define our budget as space.',
                    'instance-title-text': 'Instance title placeholder',
                    'instance-body-text': 'body-text placeholder',
                },
                {
                    'worksheet': 'allocate-resources',
                    'pane-title-text': 'Continue by creating activites to allocate to resources.',
                    'pane-body-text': '<b>Activities</b> are entities that get allocated to <b>resources</b>. When you define an activity, try '+
                    'to find a category type that best describes it from the dropdown menu. In our backpack problem, we need to allocate to different backpacks.'+
                    'Since we defined backpack as a resource, we will define a new <b>activity</b> to allocate called <b>textbook</b>. It can be best described as an <b>item</b>.',
                    'instance-title-text': '',
                    'instance-body-text': '',
                },
                {
                    'worksheet': 'contains',
                    'pane-title-text': 'Create hierarchy within your decision scenario.',
                    'pane-body-text': 'A <b>contains</b> relationship creates hierarchy among <b>activities</b> or <b>resources</b> that can be used in allocation logic among instances of activites or resources. '+
                    'Note that <b>contains</b> relationships can only be established between activity-activity or resource-resource.',
                    'instance-title-text': '',
                    'instance-body-text': '',
                },
                {
                    'worksheet': 'constrain-allocations',
                    'pane-title-text': 'Create logic for allocating instance-level activities and resources.',
                    'pane-body-text': 'In some decision scenarios, it will be necessary to impose logic upon allocation relationships. In this example, we impose ' +
                    'a condition that only allows a zipped pocket to be allocated to a pencil if a backpack that contains the pocket has been allocated to a textbook. ' +
                    'In everyday language, it does not do much good to have a pencil if you do not have a textbook to read problem sets from.',
                    'instance-title-text': '',
                    'instance-body-text': '',
                }
            ],
        }
    },
    emits: ['add-resource', 'add-existing-allocation', 'add-new-allocation', 'clear-graph','show-solution-modal'],
    watch: {
        '$store.state.dm3kGraph.resources': {
            deep: true,
            handler(resources) {
                resources = resources.map(x=>x.value)
                this.updateDropDown(resources, $('#resName2'));
            }
        },
        '$store.state.dm3kGraph.activities': {
            deep: true,
            handler(activities) {
                activities = activities.map(x=>x.value)
                this.updateDropDown(activities, $('#actTypeExisting'));
            }
        }
    },
    mounted(){
        this.dm3kConverter = new Dm3kConverter();
        this.changeHelperText('create-resources')
        this.changeHelperImg('create-resources')
        this.populateResourcesFromWB()
        this.populateActivitiesFromWB()
        this.$root.$on('delete-res-act', e => {
            console.log("-- update dropdowns AFTER deletion")
            console.log("e ", e)
            this.updateAllDropDowns();
        })
    }
}
</script>

<style scoped>
.hide{
    display: none;
}
</style>