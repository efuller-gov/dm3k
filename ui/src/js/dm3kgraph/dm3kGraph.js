import mxgraph from '../index';
// import _ from 'lodash';

const {
    mxGraph,
    mxEvent,
    mxCellOverlay,
    mxImage,
    mxConstants,
} = mxgraph;

export class Dm3kGraph {
    /**
     *  Make a Dm3kGraph
     *
     *  @param (div) container: the div that acts as the container for all DM3K graph objects
     */
    constructor(container) {

        let infoIcon = require('../../assets/rounded-info-icon-gray.png')
        // Disables the built-in context menu
        mxEvent.disableContextMenu(container);

        // Creates the graph inside the given container
        this.graph = new mxGraph(container);
        this.container = container;

        // Do not allow removing labels from parents
        this.graph.graphHandler.removeCellsFromParent = false;
        this.graph.setPanning(true);
        this.graph.panningHandler.useLeftButtonForPanning = true;
        this.graph.setAllowDanglingEdges(false);
        this.graph.connectionHandler.select = false;
        this.graph.centerZoom = false;

        // keep track of resources, activities, budgets, rewards, costs, allocatedLinks, and containsLinks
        this.resources = [];
        this.activities = [];
        this.allocatedLinks = [];
        this.containsLinks = [];
        this.constraints = [];

        // intialize the dicts that contain the dm3k object types
        // TODO
        this.resourceInstances = [];
        this.activityInstances = [];
        this.containsInstances = [];
        this.allocatedToInstances = [];

        this.rewards = {};
        this.budgets = {};
        this.costs = {};

        // the infoIcon
        this.infoIcon = infoIcon;

        //mxGraphView for scaling and stuff
        // this.view = new mxGraphView(this.graph);

        //in place label editing
        //this.graph.setHtmlLabels(true);
    }

    clearAll() {
        this.graph.removeCells(this.graph.getChildVertices(this.graph.getDefaultParent()))

        // keep track of resources, activities, budgets, rewards, costs, allocatedLinks, and containsLinks
        this.resources = [];
        this.activities = [];
        this.allocatedLinks = [];
        this.containsLinks = [];
        this.constraints = [];

        // intialize the dicts that contain the dm3k object types
        // TODO
        this.resourceInstances = [];
        this.activityInstances = [];
        this.containsInstances = [];
        this.allocatedToInstances = [];

        this.rewards = {};
        this.budgets = {};
        this.costs = {};
    }

    getResouceClassDetails() {
        var classList = [];
        for (let res of this.resources) {
            let resName = res.getValue();
            let geo = res.getGeometry();
            var classItem = {};
            classItem['className'] = resName;
            classItem['locX'] = geo.x;
            classItem['locY'] = geo.y;
            classItem['typeName'] = getDM3KBlockType(res);
            classItem['budgets'] = this.getAllNamesOfAttachmentsFor(resName, 'resource', 'budget');
            classItem['containsClasses'] = this.getAllNamesOfChildrenOf(resName);
            classItem['canBeAllocatedToClasses'] = this.getAllNamesOfAllocatedFrom(resName);
            classList.push(classItem)
        }
        return classList
    }

    getActivityClassDetails() {
        var classList = [];
        for (let act of this.activities) {
            let actName = act.getValue();
            let geo = act.getGeometry();
            var classItem = {};
            classItem['className'] = actName;
            classItem['locX'] = geo.x;
            classItem['locY'] = geo.y;
            classItem['typeName'] = getDM3KBlockType(act);
            classItem['rewards'] = this.getAllNamesOfAttachmentsFor(actName, 'activity', 'reward');
            classItem['costs'] = this.getAllNamesOfAttachmentsFor(actName, 'activity', 'cost');
            classItem['containsClasses'] = this.getAllNamesOfChildrenOf(actName);
            classItem['allocatedWhen'] = {}; // TODO

            classList.push(classItem)
        }
        return classList
    }

    getAllocationConstraintDetails() {
        var constraintList = [];
        for (const c of this.constraints) {
            var item = {}
            let allocationStart = c.source;
            let allocationEnd = c.target;
            item['allocationStart'] = {
                "resourceClass": allocationStart.source.getValue(),
                "activityClass": allocationStart.target.getValue()
            };
            item['allocationEnd'] = {
                "resourceClass": allocationEnd.source.getValue(),
                "activityClass": allocationEnd.target.getValue()
            };
            item['allocationConstraintType'] = c.getValue();

            constraintList.push(item);
        }
        return constraintList
    }


    addCompleteResource(newResType, newResName, newBudgetNameList, locX = null, locY = null) {
        let model = this.graph.getModel()
        if (model.getCell(newResName) != undefined){
            alert('Cannot create duplicate node. Please choose a new instance name.')
            return
        }

        var ans = {
            "success": true,
            "details": ""
        }

        // first determine the number of resources
        var numRes = Object.keys(this.resources).length;
        var xLoc = locX;
        var yLoc = locY;

        if (!xLoc) {
            xLoc = 100;
        }
        if (!yLoc) {
            yLoc = 120 * numRes;
        }

        // to completely add a resource you need to: add resource and add a budget (if it has one)
        try {
            // console.log("Adding resource to res list in graph")
            this.addResource(newResType, newResName, xLoc, yLoc, newBudgetNameList);

            let budgetNum = 0;
            for (const newBudgetName of newBudgetNameList) {
                this.addBudget(newBudgetName, newResName, budgetNum);
                budgetNum += 1;
            }
        } catch (err) {
            ans.success = false;
            ans.details = "Add resource failed: " + err;

        }
        // console.log("ANS: ", ans)
        return ans
    }

    addAllocation(newActName, existingResName, newRewardName, locX = null, locY = null) {
        let actCell = this.getActivity(newActName)
        let newActType = actCell.getId()

        let resInstance = this.resourceInstances.filter(x => x.label == existingResName)[0]
        let budgetNames = resInstance.budgetNameList;
        for (const budgetName of budgetNames) {
            this.addCost(budgetName, newActName, costNum);
            costNum += 1;
        }

        let costNum = Object.keys(this.costs).length

        console.log("ADD ALLOCATION IS CALLED")
        console.log("----> Cost num: ", costNum)
        console.log("this.costs ", this.costs)
        console.log("---->Object.keys(this.costs) ", Object.keys(this.costs))
        var ans = {
            "success": true,
            "details": ""
        }

        // first determine the number of resources
        // let model = this.graph.getModel()
        let existingResGeo = this.getResource(existingResName).getGeometry()
        var numAct = Object.keys(this.activities).length;
        var xLoc = locX;
        var yLoc = locY;

        if (!xLoc) {
            xLoc = existingResGeo.x + 450;
        }
        if (!yLoc) {
            yLoc = 120 * numAct;
        }

        try {
            // Throw alert if user is trying to allocate a resource without a cost. 
            //// Note: Resources without costs are meant to solely be used as containers
            if (this.resourceInstances.filter(x => x.label == existingResName)[0].budgetLabel == '') {
                alert('You cannot allocate a resource without a budget. Non-budgeted resources are only intended to be containers.')
                return
            }

            // let resInstance = this.resourceInstances.filter(x => x.label == existingResName)[0]
            // let budgetNames = resInstance.budgetNameList;
            // console.log(budgetNames)

            for (const budgetName of budgetNames) {
                this.addCost(budgetName, newActName, costNum);
                costNum += 1;
            }
            // Check to see if activity already exists
            if (this.getActivityInstance(newActName) == undefined) {
                // console.log('New Activity');
                this.addActivity(newActType, newActName, xLoc, yLoc, budgetNames);
            } else {
                console.log('ACTIVITY ALREADY EXISTS');
            }

            if (newRewardName == undefined) {
                console.log("Activity does not have a reward");
            } else {
                let rewardNames = this.getAllNamesOfAttachmentsFor(newActName, 'activity', 'reward');

                // check to see if reward already exists
                if (rewardNames.includes(newRewardName)) {
                    console.log("reward name '" + newRewardName + "' already exists")
                } else {
                    this.addReward(newRewardName, newActName);
                }

            }

            // for (const budgetName of budgetNames) {
            //     this.addCost(budgetName, newActName, costNum);
            //     costNum += 1;
            // }

            if (existingResName.length > 0) {
                this.addCanBeAllocatedTo(existingResName, newActName);
            } else {
                console.log("Didnt find allocated link for " + existingResName);
            }
        } catch (err) {
            ans.success = false;
            ans.details = "Add activity failed: " + err;
            console.log("ERROR: Add Activity failed: " + err)

        }

        return ans
    }

    addCompleteActivity(newActType, newActName, existingResName, newRewardName, costNum, locX = null, locY = null) {
        let model = this.graph.getModel()
        if (model.getCell(newActName) != undefined){
            alert('Cannot create duplicate allocation.')
            return
        }
        let ans = {
            "success": true,
            "details": ""
        }

        // first determine the number of resources
        let existingResGeo = this.getResource(existingResName).getGeometry()
        let numAct = Object.keys(this.activities).length;
        let xLoc = locX;
        let yLoc = locY;

        if (!xLoc) {
            xLoc = existingResGeo.x + 450;
        }
        if (!yLoc) {
            yLoc = 120 * numAct;
        }

        // to completely add an activity you need to:
        //   add activity,
        //   add reward (if it has one),
        //   add a allocates link (if there is a resource)
        //   add a cost (if there is a resource)


        try {
            // Throw alert if user is trying to allocate a resource without a cost. 
            //// Note: Resources without costs are meant to solely be used as containers
            if (this.resourceInstances.filter(x => x.label == existingResName)[0].budgetLabel == '') {
                alert('You cannot allocate a resource without a budget. Non-budgeted resources are only intended to be containers.')
                return
            }

            let resInstance = this.resourceInstances.filter(x => x.label == existingResName)[0]
            let budgetNames = resInstance.budgetNameList;
            // console.log(budgetNames)

            // Check to see if activity already exists
            if (this.getActivityInstance(newActName) == undefined) {
                // console.log('New Activity');
                this.addActivity(newActType, newActName, xLoc, yLoc, budgetNames);
            } else {
                // console.log('ACTIVITY ALREADY EXISTS');
            }

            if (newRewardName == undefined) {
                // console.log("Activity does not have a reward");
            } else {
                let rewardNames = this.getAllNamesOfAttachmentsFor(newActName, 'activity', 'reward');

                // check to see if reward already exists
                if (rewardNames.includes(newRewardName)) {
                    // console.log("reward name '" + newRewardName + "' already exists")
                } else {
                    this.addReward(newRewardName, newActName);
                }
            }

            for (const budgetName of budgetNames) {
                this.addCost(budgetName, newActName, costNum);
                costNum += 1;
            }

            if (existingResName.length > 0) {
                this.addCanBeAllocatedTo(existingResName, newActName);
            } else {
                // console.log("Didnt find allocated link for " + existingResName);
            }
        } catch (err) {
            ans.success = false;
            ans.details = "Add activity failed: " + err;
            // console.log("ERROR: Add Activity failed: " + err)

        }

        return ans
    }

    getResource(resName) {
        // console.log("getResources ", this.resources)
        let resource = null;
        this.resources.forEach(function(res) {
            if (res.getValue() == resName) {
                resource = res;
            }
        });
        return resource
    }

    getActivity(actName) {
        let activity = null;
        this.activities.forEach(function(act) {
            if (act.getValue() == actName) {
                activity = act;
            }
        });
        return activity
    }

    addResource(typeName, blockName, xLoc, yLoc, budgetNameList) {
        // console.log("Add resource in graph Javascript.")
        if (this.doesNameExist(blockName)) {
            throw "Cannot use name: " + blockName + " it is already taken"
        } else {
            var resColor = '#E9EDF2';
            var newRes = addDM3KResAct(this.container, this.graph, true, typeName, blockName, xLoc, yLoc, this.infoIcon, resColor);
            this.resources.push(newRes);
            this.resourceInstances.push(new ResourceInstance(typeName, blockName, budgetNameList))
        }
    }

    addActivity(typeName, blockName, xLoc, yLoc, costNameList) {
        // console.log('Adding Activity: ' + blockName + ' at ' + xLoc + ',' + yLoc);
        if (this.doesNameExist(blockName)) {
            throw "Cannot use name: " + blockName + " it is already taken"
        } else {
            var actColor = '#F2EFE9';
            var newAct = addDM3KResAct(this.container, this.graph, false, typeName, blockName, xLoc, yLoc, this.infoIcon, actColor);
            this.activities.push(newAct);
            this.activityInstances.push(new ActivityInstance(typeName, blockName, costNameList))

            //console.log(this.activities);
        }
    }

    addBudget(budgetName, resName, budgetNum) {

        // TODO - what about multiple budgets

        // find the resource
        var res = this.getResource(resName);

        var newBudget = addDM3KBudget(this.graph, budgetName, res, budgetNum);
        this.budgets[(resName + '_' + budgetName)] = newBudget;

        this.resourceInstances.filter(x => x.label == resName)[0].budgetLabel = budgetName
    }

    // TODO remove this as cost won't directly be set anymore?
    addCost(costName, actName, costNum) {
        // find the activity
        console.log('------> addCost for ', costName)
        let act = this.getActivity(actName);
        let newCost = addDM3KCost(this.graph, costName, act, costNum);
        this.costs[(actName + '_' + costName)] = newCost;


    }

    addReward(rewardName, actName) {
        // console.log("Adding Reward " + rewardName + " to activity " + actName);
        // TODO - what about multiple rewards

        // find the activity
        let act = this.getActivity(actName);

        let newReward = addDM3KReward(this.graph, rewardName, act);
        this.rewards[(actName + '_' + rewardName)] = newReward;

        this.activityInstances.filter(x => x.label == actName)[0].rewardName = rewardName
    }

    addCanBeAllocatedTo(resName, actName) {
        // console.log("Adding 'allocatedTo' link between " + resName + " and " + actName)

        var res = null;
        var act = null;

        // find the resource
        res = this.getResource(resName);

        // find the activity
        act = this.getActivity(actName);

        var newLink = addDM3KAllocatedEdge(this.container, this.graph, res, act, this.infoIcon)
        this.allocatedLinks.push(newLink);

        this.activityInstances.filter(x => x.label == actName)[0].costLabel = this.resourceInstances.filter(x => x.label == resName)[0].budgetLabel

        // set up the allocated to instance
        // var ri = this.getResourceInstance(resName);
        var ai = new AllocationInstance(resName, actName);
        this.allocatedToInstances.push(ai);
    }

    getResourceInstance(resName) {
        return this.resourceInstances.filter(x => x.label == resName)[0]
    }

    getActivityInstance(actName) {
        return this.activityInstances.filter(x => x.label == actName)[0]
    }

    getContainsInstance(parentName, childName) {
        return this.containsInstances.filter(x => (x.parentName == parentName) && (x.childName == childName))[0]
    }

    getAllocatedToInstance(resName, actName) {
        return this.allocatedToInstances.filter(x => (x.resName == resName) && (x.actName == actName))[0]
    }

    addContains(parentName, childName) {

        var p = null;
        var c = null;
        var type = 'resource';

        // find the parent...dunno if its resource or activity
        if (this.isResource(parentName)) {
            p = this.getResource(parentName);
            c = this.getResource(childName);
        } else {
            // assume if not resource this is activity, check done at higher level
            type = 'activity'
            p = this.getActivity(parentName);
            c = this.getActivity(childName);
        }

        var newLink = addDM3KContainsEdge(this.container, this.graph, p, c, this.infoIcon)
        this.containsLinks.push(newLink);

        // set up the contains instance
        var ci = new ContainsInstance(parentName, childName, type);
        this.containsInstances.push(ci);
    }

    addNewActContains(parentType, parentName, childName, rewardName) {

        // get the geometry and location - size the parent is new, base off the child
        let existingGeo = this.getActivity(childName).getGeometry();
        let xLoc = existingGeo.x + 300;
        let yLoc = existingGeo.y + 200;

        // Check to see if activity already exists
        if (this.getActivityInstance(parentName) == undefined) {
            // console.log('New Activity')
            this.addActivity(parentType, parentName, xLoc, yLoc, []); // empty list budget names since not connected to resource  
        } else {
            // console.log('ACTIVITY ALREADY EXISTS')
        }

        // add the reward if there is a reward name
        if (rewardName.length > 0) {
            this.addReward(rewardName, parentName);
        }

        // add the contains edge
        this.addContains(parentName, childName)
    }

    addNewResContains(parentType, parentName, childName) {

        // get the geometry and location - size the parent is new, base off the child
        let existingGeo = this.getResource(childName).getGeometry();
        let xLoc = existingGeo.x - 300;
        let yLoc = existingGeo.y - 200;

        // Check to see if activity already exists
        if (this.getResourceInstance(parentName) == undefined) {
            // console.log('New Resource')
            this.addResource(parentType, parentName, xLoc, yLoc, []); // empty list budget names since not connected to resource  
        } else {
            // console.log('RESOURCE ALREADY EXISTS')
        }

        // add the contains edge
        this.addContains(parentName, childName)
    }

    addConstraint(allocation1FromName, allocation1ToName, allocation2FromName, allocation2ToName, constraintType) {
        console.log('Adding Constraint from ' + allocation1FromName + '->' + allocation1ToName + ' to ' + allocation2FromName + '->' + allocation2ToName);
        console.log('  constraintType: ' + constraintType);
        var a1 = this.getAllocation(allocation1FromName, allocation1ToName);
        var a2 = this.getAllocation(allocation2FromName, allocation2ToName);

        console.log('Allocation1: ' + a1);
        console.log('Allocation2: ' + a2);

        var newConstraint = addDM3KConstraintEdge(this.container, this.graph, a1, a2, constraintType);
        this.constraints.push(newConstraint);

        console.log('New Constraint');
        console.log(newConstraint);

    }

    /*  getType(name) {
         var type = 'unknown';

         if (name in this.resources) {
             type = 'resource';
         }
         else if (name in this.activities) {
             type = 'actvitiy';
         }
         else if (name in this.containsLinks) {
             type = 'containsLink'
         }
         else if (name in this.allocatedLinks) {
             type = 'allocatedLink'
         }

         return type
     } */

    isResource(name) {
        return this.getAllNamesOfType('resource').includes(name)
    }

    isActivity(name) {
        return this.getAllNamesOfType('activity').includes(name)
    }

    getAllNamesOfType(typeName) {
        var names = []
        if (typeName == 'resource') {
            this.resources.forEach(function(res) {
                names.push(res.getValue())
            });
        } else if (typeName == 'activity') {
            this.activities.forEach(function(act) {
                names.push(act.getValue())
            });
        } else {
            throw "type name: " + typeName + " is not found in graph (try using 'resource' or 'activity'";
        }
        return names
    }

    getAllNamesOfChildrenOf(parentName) {
        var names = [];
        this.containsLinks.forEach(function(link) {
            let linkParentName = link.source.getValue();
            let linkChildName = link.target.getValue();
            if (linkParentName == parentName) {
                names.push(linkChildName);
            }
        });
        return names
    }

    getAllocation(fromName, toName) {
        console.log("FINDING ALLOCATION: " + fromName + "->" + toName);
        console.log(this.allocatedLinks)
        let allocation = null;
        this.allocatedLinks.forEach(function(link) {
            let linkResName = link.source.getValue();
            let linkActName = link.target.getValue();
            console.log("   existingAllocation: " + linkResName + "->" + linkActName);
            if ((linkResName == fromName) && (linkActName == toName)) {
                allocation = link;
            }
        });
        return allocation
    }

    getAllNamesOfAllocatedFrom(resName) {
        var names = [];
        this.allocatedLinks.forEach(function(link) {
            let linkResName = link.source.getValue();
            let linkActName = link.target.getValue();
            if (linkResName == resName) {
                names.push(linkActName);
            }
        });
        return names
    }

    getAllNamesOfAttachmentsFor(resActName, resOrAct, attachmentType) {
        var names = []
        var res = ''
        if (resOrAct == 'resource') {
            res = this.getResource(resActName);
        } else {
            res = this.getActivity(resActName);
        }

        // get all edges of the block
        for (let i = 0; i < res.getEdgeCount(); i++) {
            let edge = res.getEdgeAt(i);
            let vertexType = getDM3KBlockType(edge.target);
            if (vertexType == attachmentType) {
                names.push(edge.target.getValue());
            }
        }
        return names
    }

    doesNameExist(name) {
        let nameArray = []
        for (const key of Object.keys(this.graph.model.cells)) {
            let cell = this.graph.model.cells[key];
            // named items should be vertexs and be a child of the default parent
            if (cell.isVertex() && (cell.getParent() == this.graph.getDefaultParent())) {
                nameArray.push(cell.getValue())
            }
        }
        return nameArray.includes(name)
    }

    doesActivityExist(name) {
        let nameArray = [];
        // let activity = undefined
        this.activities.forEach(function(act) {
            nameArray.push(act.getValue())
        });
        return nameArray.includes(name)
    }

    doesResourceExist(name) {
        let nameArray = []
        this.resources.forEach(function(res) {
            nameArray.push(res.getValue())
        });
        return nameArray.includes(name)
    }


}

// ********************************************************************* //
// ********************************************************************* //
// ********************************************************************* //
// ********************************************************************* //
// ********************************************************************* //

function addDM3KResAct(container, graph, isResource, typeName, blockName, xLoc, yLoc, infoIcon, color) {
    const width = 150;
    const height = 100;
    const blockStyle = 'fontStyle=1;fontColor=#707070;fontSize=20;fillColor=' + color + ';strokeColor=#E9EDF2';
    const typeStyle = 'fontStyle=2;fontColor=#707070;fontSize=12;';
    const typeSize = 0;
    const typeXLoc = 0.5;
    const typeYLoc = 0.05;
    const infoIconSize = 25;
    const infoIconX = -15;
    const infoIconY = -15;
    const infoToolTip = 'click for instance information'

    var block = null;

    // Gets the default parent for inserting new cells. This
    // is normally the first child of the root (ie. layer 0).
    var parent = graph.getDefaultParent();

    // Adds cells to the model in a single step
    graph.getModel().beginUpdate();
    try {
        block = graph.insertVertex(parent, typeName, blockName, xLoc, yLoc, width, height, blockStyle);
        // var typeLabel = graph.insertVertex(block, blockName, typeName, typeXLoc, typeYLoc, typeSize, typeSize, typeStyle, true);
        graph.insertVertex(block, blockName, typeName, typeXLoc, typeYLoc, typeSize, typeSize, typeStyle, true);
        var iCircle = new mxCellOverlay(new mxImage(infoIcon, infoIconSize, infoIconSize), infoToolTip);


        // the overlay point to be within the resource box
        var pt = iCircle.offset;
        pt.x = infoIconX;
        pt.y = infoIconY;
        graph.addCellOverlay(block, iCircle);

        // detect click on the circle-i
        iCircle.addListener(mxEvent.CLICK, function(sender, evt) {
            var cell = evt.getProperty('cell');
            var cellType = 'Activity';
            var budgetName = [];
            var costName = [];
            var rewardName = ''
            var connectedBoxIDs, connectedBoxNames = [];

            if (isResource) {
                cellType = 'Resource';

                connectedBoxIDs = cell.edges.map(x => x.target.getId()); // dont think reward and cost use cell.id like act and res!!!
                connectedBoxNames = cell.edges.map(x => x.target.getValue());
                for (let i = 0; i < connectedBoxIDs.length; i++) {
                    if (connectedBoxIDs[i].startsWith('budget')) {
                        budgetName.push(connectedBoxNames[i]);
                    }
                }



            } else {
                cellType = 'Activity';

                connectedBoxIDs = cell.edges.map(x => x.target.getId()); // dont think reward and cost use cell.id like act and res!!!
                connectedBoxNames = cell.edges.map(x => x.target.getValue());

                for (let i = 0; i < connectedBoxIDs.length; i++) {
                    if (connectedBoxIDs[i].startsWith('reward')) {
                        rewardName = connectedBoxNames[i];
                    }
                    if (connectedBoxIDs[i].startsWith('cost')) {
                        costName.push(connectedBoxNames[i]);
                    }
                }

            }
            var event = new CustomEvent(
                'CircleIClicked', {
                    detail: {
                        id: cell.id,
                        name: cell.value,
                        type: cellType,
                        budget: budgetName,
                        cost: costName,
                        reward: rewardName
                    },
                    bubbles: true,
                    cancelable: true

                }
            );
            container.dispatchEvent(event)
        });
    } finally {
        // Update the display
        graph.getModel().endUpdate();
    }

    return block;
}

/**
 *  Adds a budget block to the DM3K graph
 *
 *  @param (mxGraph) graph: an mxGraph object (e.g var graph = new mxGraph(container);)
 *  @param (string) budgetName: the name of the budget block (this is name in text in the middle of block)
 *  @param (mxCell) res: a vertex in the mxGraph representing a resource
 *
 *  @return (mxCell) block: a vertex in the mxGraph representing a budget
 */
function addDM3KBudget(graph, budgetName, res, budgetNum) {
    const width = 85;
    const height = 60;
    const space = 20; // space between budget and resource
    const blockStyle = 'fontStyle=1;fontColor=#707070;fontSize=14;fillColor=#E9EDF2;strokeColor=#E9EDF2;';
    const typeStyle = 'fontStyle=2;fontColor=#707070;fontSize=10;';
    const typeSize = 0;
    const typeXLoc = 0.5;
    const typeYLoc = 0.05;
    const edgeStyle = 'defaultEdge;endArrow=none;startArrow=none;strokeColor=darkgray;strokeWidth=2;';

    // place the budget to the left of the resource
    // get the location of the resource
    var xLoc = res.geometry.x - space - width;
    var yLoc = res.geometry.y + budgetNum * (space + height);

    var block = null;

    // Gets the default parent for inserting new cells. This
    // is normally the first child of the root (ie. layer 0).
    var parent = graph.getDefaultParent();

    // Adds cells to the model in a single step
    graph.getModel().beginUpdate();
    try {
        block = graph.insertVertex(parent, 'budget.' + budgetName + '.' + budgetNum, budgetName, xLoc, yLoc, width, height, blockStyle);
        // var typeLabel = graph.insertVertex(block, null, 'budget', typeXLoc, typeYLoc, typeSize, typeSize, typeStyle, true);
        graph.insertVertex(block, null, 'budget', typeXLoc, typeYLoc, typeSize, typeSize, typeStyle, true);

        // link = graph.insertEdge(parent, null, '', res, block, edgeStyle);
        graph.insertEdge(parent, null, '', res, block, edgeStyle);

    } finally {
        // Update the display
        graph.getModel().endUpdate();
    }

    return block;
}

/**
 *  Adds a cost block to the DM3K graph
 *
 *  @param (mxGraph) graph: an mxGraph object (e.g var graph = new mxGraph(container);)
 *  @param (string) costName: the name of the cost block (this is name in text in the middle of block)
 *  @param (mxCell) act: a vertex in the mxGraph representing a activity
 *
 *  @return (mxCell) block: a vertex in the mxGraph representing a cost
 */
function addDM3KCost(graph, costName, act, costNum) {
    console.log("----> addDM3KCost ")
    console.log("---> costNum ", costNum)
    const width = 65;
    const height = 40;
    const space = 20; // space between cost and activity
    const blockStyle = 'fontStyle=1;fontColor=#707070;fontSize=10;fillColor=#F2EFE9;strokeColor=#F2EFE9;';
    const typeStyle = 'fontStyle=2;fontColor=#707070;fontSize=8;';
    const typeSize = 0;
    const typeXLoc = 0.5;
    const typeYLoc = 0.05;
    const edgeStyle = 'defaultEdge;endArrow=none;startArrow=none;strokeColor=darkgray;strokeWidth=2;';

    // place the budget to the right of the activity near the top
    //var xLoc = act.geometry.x + act.geometry.width + space;
    //var yLoc = act.geometry.y;

    var xLoc = act.geometry.x + act.geometry.width + space;
    var yLoc = act.geometry.y + height + space + (height + space / 2) * costNum;

    var block = null;

    // Gets the default parent for inserting new cells. This
    // is normally the first child of the root (ie. layer 0).
    var parent = graph.getDefaultParent();

    // Adds cells to the model in a single step
    graph.getModel().beginUpdate();
    try {
        block = graph.insertVertex(parent, 'cost.' + costName + '.' + costNum, costName, xLoc, yLoc, width, height, blockStyle);
        // var typeLabel = graph.insertVertex(block, null, 'cost', typeXLoc, typeYLoc, typeSize, typeSize, typeStyle, true);
        graph.insertVertex(block, null, 'cost', typeXLoc, typeYLoc, typeSize, typeSize, typeStyle, true);

        // link = graph.insertEdge(parent, null, '', act, block, edgeStyle);
        graph.insertEdge(parent, null, '', act, block, edgeStyle);

    } finally {
        // Update the display
        graph.getModel().endUpdate();
    }
    // This is a bug fix. Manually setting the id.
    block.setId('cost')
    return block;
}

/**
 *  Adds a reward block to the DM3K graph
 *
 *  @param (mxGraph) graph: an mxGraph object (e.g var graph = new mxGraph(container);)
 *  @param (string) rewardName: the name of the reward block (this is name in text in the middle of block)
 *  @param (mxCell) act: a vertex in the mxGraph representing a activity
 *
 *  @return (mxCell) block: a vertex in the mxGraph representing a reward
 */
function addDM3KReward(graph, rewardName, act) {
    const width = 65;
    const height = 40;
    const space = 20; // space between cost and activity
    const blockStyle = 'fontStyle=1;fontColor=#707070;fontSize=10;fillColor=#F2EFE9;strokeColor=#F2EFE9;';
    const typeStyle = 'fontStyle=2;fontColor=#707070;fontSize=8;';
    const typeSize = 0;
    const typeXLoc = 0.5;
    const typeYLoc = 0.05;
    const edgeStyle = 'defaultEdge;endArrow=none;startArrow=none;strokeColor=darkgray;strokeWidth=2;';

    // place the reward to the right of the resource near the bottom
    var xLoc = act.geometry.x + act.geometry.width + space;
    var yLoc = act.geometry.y - height / 4 + space / 2;

    var block = null;

    // Gets the default parent for inserting new cells. This
    // is normally the first child of the root (ie. layer 0).
    var parent = graph.getDefaultParent();

    // Adds cells to the model in a single step
    graph.getModel().beginUpdate();
    try {
        block = graph.insertVertex(parent, 'reward.' + act.getValue() + '.' + rewardName, rewardName, xLoc, yLoc, width, height, blockStyle);
        // var typeLabel = graph.insertVertex(block, null, 'reward', typeXLoc, typeYLoc, typeSize, typeSize, typeStyle, true);
        graph.insertVertex(block, null, 'reward', typeXLoc, typeYLoc, typeSize, typeSize, typeStyle, true);

        // link = graph.insertEdge(parent, null, '', act, block, edgeStyle);
        graph.insertEdge(parent, null, '', act, block, edgeStyle);


    } finally {
        // Update the display
        graph.getModel().endUpdate();
    }
    block.setId('reward')
    return block;
}


/**
 *  Adds a 'can be allocated to' edge between two blocks
 *
 *  @param (mxGraph) graph: an mxGraph object (e.g var graph = new mxGraph(container);)
 *  @param (mxCell) res: a vertex in the mxGraph representing a resource
 *  @param (mxCell) act: a vertex in the mxGraph representing an activity
 *  @param (string) infoIcon: the folder path to the info-icon graphic
 *
 *  @return (mxCell) edge: an edge in the mxGraph representing the 'can be allocated to' link
 */
function addDM3KAllocatedEdge(container, graph, res, act, infoIcon) {
    const edgeStyle = 'defaultEdge;verticalAlign=bottom;verticalLabelPosition=top;fontColor=#707070;strokeColor=darkgray;strokeWidth=2;';
    const infoIconSize = 15;
    const infoIconX = 60;
    const infoIconY = -10;
    const infoToolTip = 'click for instance information'

    var edge = null;

    // Gets the default parent for inserting new cells. This
    // is normally the first child of the root (ie. layer 0).
    var parent = graph.getDefaultParent();

    // Adds cells to the model in a single step
    graph.getModel().beginUpdate();
    try {
        edge = graph.insertEdge(parent, null, 'can be allocated to', res, act, edgeStyle)
        var iCircle = new mxCellOverlay(new mxImage(infoIcon, infoIconSize, infoIconSize), infoToolTip);
        var pt = iCircle.offset;
        pt.x = infoIconX;
        pt.y = infoIconY;
        graph.addCellOverlay(edge, iCircle);

        // Adds animation to edge shape and makes "pipe" visible
        //dm3kgraph.state.shape.node.getElementsByTagName('path')[0].removeAttribute('visibility');
        //dm3kgraph.state.shape.node.getElementsByTagName('path')[0].setAttribute('stroke-width', '6');
        //dm3kgraph.state.shape.node.getElementsByTagName('path')[0].setAttribute('stroke', 'lightGray');
        edge.setAttribute('class', 'flow');

        // detect click on the circle-i
        iCircle.addListener(mxEvent.CLICK, function(sender, evt) {
            var cell = evt.getProperty('cell');
            console.log("Circle-I of 'can be allocated to' link from: " + cell.source.value + " to " + cell.target.value);

            var event = new CustomEvent(
                'CircleIClicked', {
                    detail: {
                        id: cell.id,
                        name: cell.source.value + "_" + cell.target.value,
                        type: 'AllocatedTo',
                        resourceName: cell.source.value,
                        activityName: cell.target.value
                    },
                    bubbles: true,
                    cancelable: true
                }
            );
            container.dispatchEvent(event)

        });

    } finally {
        // Update the display
        graph.getModel().endUpdate();
    }

    return edge;
}

/**
 *  Adds a 'contains' edge between two blocks
 *
 *  @param (mxGraph) graph: an mxGraph object (e.g var graph = new mxGraph(container);)
 *  @param (mxCell) parentBlock: a vertex in the mxGraph representing a resource or activity that is parent or container
 *  @param (mxCell) childBlock: a vertex in the mxGraph representing a resource or activity that is child on thing contained
 *  @param (string) infoIcon: the folder path to the info-icon graphic
 *
 *  @return (mxCell) edge: an edge in the mxGraph representing the 'can be allocated to' link
 */
function addDM3KContainsEdge(container, graph, parentBlock, childBlock, infoIcon) {
    const edgeStyle = 'defaultEdge;verticalAlign=bottom;verticalLabelPosition=top;fontColor=#707070;strokeColor=darkgray;strokeWidth=2;';
    const infoIconSize = 15;
    const infoIconX = 30;
    const infoIconY = -10;
    const infoToolTip = 'click for instance information'

    var edge = null;

    // Gets the default parent for inserting new cells. This
    // is normally the first child of the root (ie. layer 0).
    var parent = graph.getDefaultParent();

    // Adds cells to the model in a single step
    graph.getModel().beginUpdate();
    try {
        edge = graph.insertEdge(parent, null, 'contains', parentBlock, childBlock, edgeStyle)
        var iCircle = new mxCellOverlay(new mxImage(infoIcon, infoIconSize, infoIconSize), infoToolTip);
        var pt = iCircle.offset;
        pt.x = infoIconX;
        pt.y = infoIconY;
        graph.addCellOverlay(edge, iCircle);

        // detect click on the circle-i
        iCircle.addListener(mxEvent.CLICK, function(sender, evt) {
            var cell = evt.getProperty('cell');
            console.log("Circle-I of 'contains' link from: " + cell.source.value + " to " + cell.target.value);

            var event = new CustomEvent(
                'CircleIClicked', {
                    detail: {
                        id: cell.id,
                        name: cell.source.value + "_" + cell.target.value,
                        type: 'Contains',
                        parentName: cell.source.value,
                        childName: cell.target.value
                    },
                    bubbles: true,
                    cancelable: true
                }
            );
            container.dispatchEvent(event)

        });
    } finally {
        // Update the display
        graph.getModel().endUpdate();
    }

    return edge;
}

function addDM3KConstraintEdge(container, graph, allocatedLink1, allocatedLink2, constraintType) {
    //const edgeStyle = 'defaultEdge;verticalAlign=bottom;verticalLabelPosition=top;fontColor=#707070;strokeColor=blue;strokeWidth=2;';
    const edgeStyle = 'defaultEdge';
    // const infoIconSize = 15;

    var edge = null;

    // Gets the default parent for inserting new cells. This
    // is normally the first child of the root (ie. layer 0).
    var parent = graph.getDefaultParent();

    // Adds cells to the model in a single step
    graph.getModel().beginUpdate();
    try {
        edge = graph.insertEdge(parent, null, constraintType, allocatedLink1, allocatedLink2, edgeStyle)

        // properties for Edge
        graph.setCellStyles(mxConstants.STYLE_STROKECOLOR, 'blue', [edge]) // make the line color blue
        graph.setCellStyles(mxConstants.STYLE_STROKEWIDTH, 1, [edge]) // stroke size in pixels
        graph.setCellStyles(mxConstants.STYLE_DASHED, 1, [edge]) // set to dashed
        graph.setCellStyles(mxConstants.ARROW_SIZE, 20, [edge]) // make the arrow smaller (default = 30)
        graph.setCellStyles(mxConstants.STYLE_ENDARROW, mxConstants.ARROW_OPEN, [edge])
        graph.setCellStyles(mxConstants.STYLE_STARTARROW, mxConstants.ARROW_OVAL, [edge])

        // properties for label
        graph.setCellStyles(mxConstants.STYLE_FONTCOLOR, 'blue', [edge])
        graph.setCellStyles(mxConstants.STYLE_FONTSIZE, 9, [edge]) // fontsize in pixels
        graph.setCellStyles(mxConstants.STYLE_VERTICAL_ALIGN, mxConstants.ALIGN_TOP, [edge]) // how is label aligned verically, set to top
        graph.setCellStyles(mxConstants.STYLE_ALIGN, mxConstants.ALIGN_LEFT, [edge]) // how is label aligned horizontally, set to left
        graph.setCellStyles(mxConstants.STYLE_LABEL_POSITION, mxConstants.ALIGN_RIGHT, [edge]) // how is the label position horizontally aligned
        graph.setCellStyles(mxConstants.STYLE_VERTICAL_LABEL_POSITION, mxConstants.ALIGN_TOP, [edge])

        // properties for change
        graph.setCellStyles(mxConstants.STYLE_EDITABLE, 0, [edge]) // you cant edit the text of the link
        graph.setCellStyles(mxConstants.STYLE_MOVABLE, 0, [edge]) // you cant move the edge
        graph.setCellStyles(mxConstants.STYLE_RESIZABLE, 0, [edge]) // you cant resize the edge

    } finally {
        // Update the display
        graph.getModel().endUpdate();
    }

    return edge;
}

//
//  Utility Functions
//
// function getDM3KBlockLocationSize(block) {
//     return [block.geometry.x, block.geometry.y, block.geometry.width, block.geometry.height]
// }

function getDM3KBlockType(block) {
    // we assume that type is always the name of the first child vertex in the block
    let typeLabel = block.getChildAt(0);

    // we assume that the type name is the value of the child
    return typeLabel.getValue();
}



// ********************************************************************* //
// ********************************************************************* //
// ********************************************************************* //
// ********************************************************************* //
// ********************************************************************* //

/**
 *  Class definitions for instances of resources and activities.
 **/

class AllocationInstance {

    constructor(resClassName, actClassName) {
        this.resName = resClassName;
        this.actName = actClassName;
        this.instanceTableData = [];
        this.addToInstanceTable('ALL', 'ALL')
    }

    addToInstanceTable(resInstanceName, actInstanceName) {
        this.instanceTableData.push({resourceInstance: resInstanceName,
                                     activityInstance: actInstanceName});
    }

    clearInstanceTable() {
        this.instanceTableData = [];
    }

    getDetails() {
        var detailList = {
            "resourceClassName": this.resName,
            "activityClassName": this.actName,
            "instanceTable": []
        };
        for (let instance of this.instanceTableData) {
            let details = {
                
                "resourceInstanceName": instance.resourceInstance,
                "activityInstanceName": instance.activityInstance 
            }
            detailList.instanceTable.push(details);
        }
        return detailList 
    }
}

class ContainsInstance {

    constructor(parentName, childName, parentType) {
        this.parentName = parentName;
        this.childName = childName;
        this.parentType = parentType;
        this.instanceTableData = [];
        this.addToInstanceTable('ALL', 'ALL')
    }

    addToInstanceTable(parentInstanceName, childInstanceName) {
        this.instanceTableData.push({parentInstance: parentInstanceName,
                                     childInstance: childInstanceName});
    }

    clearInstanceTable() {
        this.instanceTableData = [];
    }

    getDetails() {
        var detailList = {
            "parentClassName": this.parentName,
            "childClassName": this.childName,
            "parentType": this.parentType,
            "instanceTable": []
        };
        for (let instance of this.instanceTableData) {
            let details = {
                
                "parentInstanceName": instance.parentInstance,
                "childInstanceName": instance.childInstance 
            }
            detailList.instanceTable.push(details);
        }
        return detailList 
    }
}

 class ResourceInstance {

     /**
      *  Define resource instance for storage and assignment to activities via UI.
      *
      **/

     constructor(type, label, budgetNameList) {

         this.type = type;
         this.label = label;
         this.budgetLabel = '';
         this.budgetValue = 0;
         this.budgetNameList = budgetNameList
         this.instanceTableData = [];
         this.edges = []; //activities the instance is allocated to
         this.allocated_to = 'ALL';
         let sample_name = ""+label+"_Resource_instance_0";
         this.addDefaultRow(sample_name)
         console.log("Resource Instance TableData: %O", this.instanceTableData)   
     }

    addDefaultRow(sample_name) {
        let instanceExample = {name: sample_name};
        for (const budgetName of this.budgetNameList) {
            instanceExample["budget_"+budgetName] = 1;
        }
        this.instanceTableData.push(instanceExample)
    }

    addToInstanceTable(sample_name, budgetDict) {
        let instanceExample = {name: sample_name};
        for (const budgetName in budgetDict) {
            instanceExample["budget_"+budgetName] = budgetDict[budgetName];
        }
        this.instanceTableData.push(instanceExample)
    }

    clearInstanceTable() {
        this.instanceTableData = [];
    }

    getDetails() {
        var detailList = {
            "className": this.label,
            "instanceTable": []
        }
        for (let instance of this.instanceTableData) {
            let details = {
                "instanceName": instance.name,
                "budget" : {}}
            for (let item in instance) {
                if (item.startsWith("budget")) {
                    let name = item.substring(7)  // 7 = size of 'budget_'
                    details.budget[name] = Number(instance[item]);
                }
            }
            detailList.instanceTable.push(details)
        }
        return detailList 
    }
 }

class ActivityInstance {

     /**
      *  Define activity instance for storage and assignment to activities via UI.
      *
      **/

    constructor(type, label, costNameList) {

         this.type = type;
         this.label = label;
         this.costNameList = costNameList;
         this.rewardLabel = '';
         this.rewardValue = 0;
         this.edges = []; //resource instances that are allocated to this activity instance
         let sample_name = ""+label+"_Activity_instance_0";
         this.instanceTableData = [];
         this.addDefaultRow(sample_name)

     }

    addDefaultRow(sample_name) {
        let instanceExample = {name: sample_name, reward: 1};
        for (const costName of this.costNameList) {
            instanceExample["cost_"+costName] = 1;
        }
        this.instanceTableData.push(instanceExample)
    }

    addToInstanceTable(sample_name, rewards, costDict) {
        let instanceExample = {name: sample_name, reward: rewards};
        for (const costName in costDict) {
            instanceExample["cost_"+costName] =costDict[costName];
        }
        this.instanceTableData.push(instanceExample)
    }

    clearInstanceTable() {
        this.instanceTableData = [];
    }

     getDetails() {
        var detailList = {
            "className": this.label,
            "instanceTable": []
        }
        for (let instance of this.instanceTableData) {
            let details = {
                
                "instanceName": instance.name,
                "cost" : {},    
                "reward": Number(instance.reward)  // TODO - fix this when we have mulitple rewards
            }
            for (let item in instance) {
                if (item.startsWith("cost")) {
                    let name = item.substring(5);  // 5 = size of 'cost_'
                    details.cost[name] = Number(instance[item]);
                }
            }
            
            detailList.instanceTable.push(details)
        }
        return detailList 
     }

}
