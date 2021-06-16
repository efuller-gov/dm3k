<template>
    <div id="bottom-container">
        <div id="menu">
            <div id="worksheet_menu_column">
                <div id='zoom-buttons'>
					<button id="zoomIn" class='zoom-button'>+</button>
					<button id="zoomOut" class='zoom-button'>-</button>
					<!-- <b class="title-text">Version name</b> -->
				</div>
                <button @click="createResourceTab()" id="create-resources-button" type="button" class="menu-button enabled">Create resources</button>
                <button @click="allocateResourcesTab()" id="allocate-resources-button" type="button" class="menu-button disabled">Allocate resources to activities</button>
                <button @click="containsTab()" id="contains-button" type="button" class="menu-button disabled">Make contains relationship</button>
                <button id="constrain-allocations-button" type="button" class="menu-button disabled">Constrain allocations</button>
            </div>
            <div id="create-resource-column" class="left_column responsive-column-text">
                <p class="title-text"><b>Create a resource.</b></p>
                <label for="resType">My <b>resource</b> is what I am limited by. <br>It can be best described by</label>
                <select class="chosen-select" id="resType">
                    <option value="none">     </option>
                    <option value="custom input">custom input</option>
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
                        <option value="custom input">custom input</option>
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
                    <input type="button" class="done-button" value="Contains Done" id="addContains">
                </div>
                <div id="contains-new-act-submenu" class="hide">
                    <label for="actType2"> I want </label>
                    <select class="chosen-select activity-select" id="actType2" style="margin-left: 0px;" onchange="worksheetUtils_newActivityActivated()">
                        <option selected style="font-weight: bold;">a new activity</option>
                        <option value="custom input">custom input</option>
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
                    <input type="button" class="done-button" value="Contains Done" id="addNewActContains">
                </div>
                <div id="contains-new-res-submenu" class="hide">
                    <label for="resType2"> I want </label>
                    <select class="chosen-select activity-select" id="resType2" style="margin-left: 0px;" onchange="worksheetUtils_newActivityActivated()">
                        <option selected style="font-weight: bold;">a new resource</option>
                        <option value="custom input">custom input</option>
                    </select>
                    <label for="res-childName">to contain</label>
                    <select class="chosen-select" id="res-childName">
                        <!--pull from dm3kgraph.resources -->
                    </select>
                    <br><br>
                    <label id="parent-label" for="res-parentName">Label the parent </label>
                    <input type="text" id="res-parentName"><br><br>
                    <input type="button" class="done-button" value="Contains Done" id="addNewResContains">
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
                <input type="button" class="done-button" value="Done" id="addConstraint">
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
				<input type="button" class="done-button" value="Load existing diagram" onclick="getFile()"><br><br><br>
				<div style='height: 0px;width: 0px;overflow: hidden;'><input type="file" id="loadLocally" accept="application/json"></div>
				<!-- <p>Save diagram to work on later</p> -->
				<label for="diagramName">Save current diagram as </label>
				<input type="text" class="long-input" id="diagramName" value="dm3kDiagram" ><br>
				<input type="button" class="done-button" value="Save file" id="saveLocally" style="margin-top: 10px;"><br><br>
				<p><br>Click below to submit your scenario to DM3K for solving.<br>
					You may return here to edit your scenario afterwards.</p>
				<label for="algType">Algorithm Type</label>
				<select class="chosen-select" id="algType">
					<option value="KnapsackViz">Knapsack</option>
					<option value="FullHouseViz">FullHouse</option>
				</select><br>
				<label for="serverLoc">DM3K backend </label>
				<input type="text" class="long-input" id="serverLoc" value="https://10.109.11.239:8050"><br>
                <input style="margin-top: 10px;" type="button" class="done-button" value="Submit to DM3K" id="submitDM3K">
            </div>
        </div>  
    </div>
</template>

<script>
import $ from 'jquery'
import {ResourceInstance} from '../js/dm3kgraph/dataClasses';
import {ActivityInstance} from '../js/dm3kgraph/dataClasses';

export default {
    name: 'WorksheetPane',
    methods: {
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
            let newResType = $("#resType").val();
            if ( (newResType=='none') | (newResName=='')){
                alert('Please provide a label to create a new resource.')
                return
            }
            let newBudgetName = $("#budgetName").val();
            let budgetNameList = newBudgetName.split(",");
            let newBudgetNameList = budgetNameList.map(s => s.trim())  // trim in case user but in a space with comma

            let newResName = $("#resName").val();
            this.$store.state.resourceInstances.push(new ResourceInstance(newResType, newResName, budgetNameList))
            this.$emit('add-resource', 
                {
                    resType: newResType,
                    resName: newResName,
                    budgetNameList: budgetNameList,
                    newBudgetNameList: newBudgetNameList
                }
            )

            // Send completed resource input to graph
            this.resetResourcePrompt();
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

            let newActType = $("#actType").val();
            let newActName = $("#actName").val();
            let existingResName = $("#resName2").val();
            let newRewardName = $("#rewardName").val();

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
            // Allocate to existing activity
            // if ($("#actType").val() == 'a new activity'){
            if ($("#existing-allocation").hasClass("enabled")){
                let actName = $("#actTypeExisting").val();
                // TODO: push to store's allocationLinks
                this.$emit('add-existing-allocation', 
                    {
                        actName: actName,
                        existingResName: existingResName,
                        newRewardName: newRewardName,
                    }
                )
            }
            // Allocate to new activity, and create new activity
            else{
                if (newActType.includes('[')){
                    let tmp = newActType.split('[')
                    tmp = newActType.split(']',2)

                    newActType = tmp[0].split('[')[1];
                    newActName = tmp[1]
                }
                // TODO: How am I going to get the costs for activities from here?
                let costNameList = []
                this.$store.state.activityInstances.push(new ActivityInstance(newActType, newActName, costNameList))
                this.$emit('add-new-allocation', 
                    {
                        actName: newActName,
                        newActType: newActType,
                        existingResName: existingResName,
                        newRewardName: newRewardName,
                    }
                )
                console.log("store: ", this.$store.state)
            }
        this.resetResourcePrompt()
        // this.resetActivityPrompt()

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
        existingContains(){
            $('#contains-existing-submenu').removeClass('hide')
			$('#contains-new-act-submenu').addClass('hide')
			$('#contains-new-res-submenu').addClass('hide')
        },
        newResContainer(){
            $('#contains-existing-submenu').addClass('hide')
			$('#contains-new-act-submenu').removeClass('hide')
			$('#contains-new-res-submenu').addClass('hide')
        },
        newActContainer(){
            $('#contains-existing-submenu').addClass('hide')
			$('#contains-new-act-submenu').addClass('hide')
			$('#contains-new-res-submenu').removeClass('hide')
        },
        updateDropDown(resList, jQuerySelector) {
            jQuerySelector.empty();
            return resList.forEach(x => jQuerySelector.append('<option value="'+x+'">'+x+'</option>'))
        },
        worksheetUtils_newActivityActivated(){
            if ($('#actType').val() != 'a new activity'){
                $('#actTypeExisting').val('an existing activity')
                $('#actName').removeAttr('disabled');
                $('#rewardName').removeAttr('disabled');
            }
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
        }
    },
    data() {
        return{
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
    emits: ['add-resource', 'add-existing-allocation', 'add-new-allocation'],
    watch: {
        '$store.state.resources': {
            deep: true,
            handler(resources) {
                resources = resources.map(x=>x.resName)
                this.updateDropDown(resources, $('#resName2'));
            }
        },
        '$store.state.activities': {
            deep: true,
            handler(activities) {
                activities = activities.map(x=>x.actName)
                this.updateDropDown(activities, $('#actTypeExisting'));
            }
        }
    },
    mounted(){
        this.changeHelperText('create-resources')
        this.changeHelperImg('create-resources')
        this.populateResourcesFromWB()
        this.populateActivitiesFromWB()
        // this.dm3kgraph = new Dm3kGraph(document.getElementById('graphContainer'), '../assets/rounded-info-icon-gray.png')
    }
}
</script>

<style scoped>
.hide{
    display: none;
}
</style>