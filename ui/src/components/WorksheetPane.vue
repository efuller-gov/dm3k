<template>
    <div id="bottom-container">
        <div id="menu">
            <div id="worksheet_menu_column">
                <div id='zoom-buttons'>
					<button id="zoomIn" class='zoom-button'>+</button>
					<button id="zoomOut" class='zoom-button' style="margin-right: 10px;">-</button>
					<b class="title-text">APL Version</b>
				</div>
                <button id="create-resources-button" type="button" class="menu-button enabled">Create resources</button>
                <button id="allocate-resources-button" type="button" class="menu-button disabled">Allocate resources to activities</button>
                <button id="contains-button" type="button" class="menu-button disabled">Make contains relationship</button>
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
                <input type="button" class="done-button" value="Done" id="addResource">
            </div>
            <div id="allocate-resources-column" class="left_column hide">
                <p><b>Allocate resources to activities.</b></p>
                <span>
                <button id="new-allocation" type="button" class="menu-button sub-menu activity-choice">New activity <i class="arrow down"></i></button>
                <button id="existing-allocation" type="button" class="menu-button sub-menu activity-choice">Existing activity <i class="arrow down"></i></button>
                </span><br>
                <div id="activity-submenu-container" class="hide">
                    <label for="resName2">I want to allocate my</label>
                    <select class="chosen-select" id="resName2">
                        <!--pull from dm3kgraph.resources -->
                    </select>
                    <label for="actType"> to </label>
                    <select class="chosen-select activity-select" id="actType" style="margin-left: 0px;" onchange="worksheetUtils_newActivityActivated()">
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
                    <input type="button" class="done-button hide" value="Done" id="addActivity">
                </div>
            </div>
            <div id="contains-column" class="left_column hide">
                <p><b>Set up a contains relationship.</b></p>
                <span>
                <button id="existing-contains" type="button" class="menu-button sub-menu activity-choice"> Existing Containers<i class="arrow down"></i></button>
                <button id="new-activity-contains" type="button" class="menu-button sub-menu activity-choice">New Activity Container <i class="arrow down"></i></button>
                <button id="new-resource-contains" type="button" class="menu-button sub-menu activity-choice">New Resource Container <i class="arrow down"></i></button>
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
                <!-- To do: FIX these links -->
				<img id="helper-image" src="../assets/create-resource.svg">
				<p id="i-circle-explainer" class="explanatory-text">By clicking <img src="../assets/rounded-info-icon-gray.png" alt="circle-info" style="vertical-align:text-bottom;" height="20" width="auto">
					on any item, see actions that can be taken to define further relationships and instances.</p>
            </div>
            <div id="helper-info-div">
				<button id="hide-worksheet-button" class='zoom-button' onclick="worksheetUtil_hideShowWorksheet()">Hide worksheet</button>
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