import mxgraph from './index';
import _ from 'lodash';

const {
  mxGraph,
  mxEvent,
  mxCellOverlay,
  mxImage,
  mxConstants,
  mxUtils,
  mxRectangle
} = mxgraph;

export class Dm3kGraph {


     /**
      *  Make a Dm3kGraph
      *
      *  @param (div) container: the div that acts as the container for all DM3K graph objects
      */
     constructor(container, infoIcon) {

         // Disables the built-in context menu
		 mxEvent.disableContextMenu(container);

		 // Creates the graph inside the given container
         this.graph = new mxGraph(container);
         this.container = container;

		 // Enables rubberband selection
	     new mxRubberband(this.graph);

         // add mouse wheel handling
         var boundMouseWheelFunction = (function(evt, up) {
             if (up) {
                 this.graph.zoomIn();
             }
             else {
                 this.graph.zoomOut();
             }
             mxEvent.consume(evt);
         }).bind(this);
         //mxEvent.addMouseWheelListener(boundMouseWheelFunction);

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
         this.view = new mxGraphView(this.graph);

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
            classItem['allocatedWhen'] = {};  // TODO

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
             item['allocationStart'] = {"resourceClass": allocationStart.source.getValue(),
                                        "activityClass": allocationStart.target.getValue()};
             item['allocationEnd'] = {"resourceClass": allocationEnd.source.getValue(),
                                      "activityClass": allocationEnd.target.getValue()};
             item['allocationConstraintType'] = c.getValue();

             constraintList.push(item);
         }
         return constraintList
     }

     
     addCompleteResource(newResType, newResName, newBudgetNameList,locX=null, locY=null) {
         var ans = {"success": true, "details":""}

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
             this.addResource(newResType, newResName, xLoc, yLoc, newBudgetNameList);

             let budgetNum = 0;
             for (const newBudgetName of newBudgetNameList) {
                 this.addBudget(newBudgetName, newResName, budgetNum);
                 budgetNum += 1;
             }
         }
         catch(err) {
             ans.success = false;
             ans.details = "Add resource failed: "+err;

         }

         return ans
     }

     addCompleteActivity(newActType, newActName, existingResName, newRewardName, costNum, locX=null, locY=null) {
        console.log('----> addCompleteActivity')
         var ans = {"success": true, "details":""}

         // first determine the number of resources
         let model = this.graph.getModel()
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
          
         // to completely add an activity you need to:
         //   add activity,
         //   add reward (if it has one),
         //   add a allocates link (if there is a resource)
         //   add a cost (if there is a resource)


         try {
             // Throw alert if user is trying to allocate a resource without a cost. 
             //// Note: Resources without costs are meant to solely be used as containers
             if (this.resourceInstances.filter(x => x.label == existingResName)[0].budgetLabel == ''){
                alert('You cannot allocate a resource without a budget. Non-budgeted resources are only intended to be containers.')
                return
             }

            let resInstance = this.resourceInstances.filter(x => x.label == existingResName)[0]
            let budgetNames = resInstance.budgetNameList;
            console.log(budgetNames)

            // Check to see if activity already exists
            if (this.getActivityInstance(newActName) == undefined){
                console.log('New Activity');
                this.addActivity(newActType, newActName, xLoc, yLoc, budgetNames);
            }
            else {
                console.log('ACTIVITY ALREADY EXISTS');
            }

            if (newRewardName == undefined) {
                console.log("Activity does not have a reward");
            } 
            else {
                let rewardNames = this.getAllNamesOfAttachmentsFor(newActName, 'activity', 'reward');
                
                // check to see if reward already exists
                if (rewardNames.includes(newRewardName)) {
                    console.log("reward name '"+newRewardName+"' already exists")
                }
                else {
                    this.addReward(newRewardName, newActName);
                }
                 
            }
            
            for (const budgetName of budgetNames) {
                this.addCost(budgetName, newActName, costNum);
                costNum += 1;
            }
            
            if (existingResName.length > 0) {
                this.addCanBeAllocatedTo(existingResName, newActName);
            }
            else {
                console.log("Didnt find allocated link for "+existingResName);
            }
         }
         catch(err) {
             ans.success = false;
             ans.details = "Add activity failed: "+err;
             console.log("ERROR: Add Activity failed: "+err)

         }

         return ans
     }

     getResource(resName) {
         let resource = null;
         this.resources.forEach(function(res, index) {
            if (res.getValue() == resName) {
                resource = res;
            }
         });
         return resource
     }

     getActivity(actName) {
        let activity = null;
        this.activities.forEach(function(act, index) {
           if (act.getValue() == actName) {
               activity = act;
           }
        });
        return activity
     }

     getBudget(budgetName) {
        // TODO
     }

     getCost(costName) {
         // TODO
     }

     getReward(rewardName) {
         // TODO
     }

     addResource(typeName, blockName, xLoc, yLoc, budgetNameList) {
         if (this.doesNameExist(blockName)) {
            throw "Cannot use name: "+blockName+" it is already taken"
         } else {
            var resColor = '#E9EDF2';
            var newRes = addDM3KResAct(this.container, this.graph, true, typeName, blockName, xLoc, yLoc, this.infoIcon, resColor);
            this.resources.push(newRes);
            this.resourceInstances.push(new ResourceInstance(typeName, blockName, budgetNameList))
         }  
     }

     addActivity(typeName, blockName, xLoc, yLoc, costNameList) {
        console.log('Adding Activity: '+blockName+' at '+xLoc+','+yLoc);
        if (this.doesNameExist(blockName)) {
            throw "Cannot use name: "+blockName+" it is already taken"
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
         this.budgets[(resName+'_'+budgetName)] = newBudget;

         this.resourceInstances.filter(x => x.label == resName)[0].budgetLabel = budgetName
     }

     // TODO remove this as cost won't directly be set anymore?
     addCost(costName, actName, costNum) {
         // find the activity
         console.log('------> addCost for ', costName)
         let act = this.getActivity(actName);
         let newCost = addDM3KCost(this.graph, costName, act, costNum);
         this.costs[(actName+'_'+costName)] = newCost;


     }

     addReward(rewardName, actName) {
        console.log("Adding Reward "+rewardName+" to activity "+actName);
         // TODO - what about multiple rewards

         // find the activity
         let act = this.getActivity(actName);

         let newReward = addDM3KReward(this.graph, rewardName, act);
         this.rewards[(actName+'_'+rewardName)] = newReward;

         this.activityInstances.filter(x => x.label == actName)[0].rewardName = rewardName
     }

     addCanBeAllocatedTo(resName, actName) {
        console.log("Adding 'allocatedTo' link between "+resName+" and "+actName)

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
         var ri = this.getResourceInstance(resName);
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
        console.log(this.allocatedToInstances) 
        console.log(resName)
        console.log(actName)
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
        if (this.getActivityInstance(parentName) == undefined){
            console.log('New Activity')
            this.addActivity(parentType, parentName, xLoc, yLoc, []);   // empty list budget names since not connected to resource  
        }
        else {
            console.log('ACTIVITY ALREADY EXISTS')
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
        if (this.getResourceInstance(parentName) == undefined){
            console.log('New Resource')
            this.addResource(parentType, parentName, xLoc, yLoc, []);   // empty list budget names since not connected to resource  
        }
        else {
            console.log('RESOURCE ALREADY EXISTS')
        }
        
        // add the contains edge
        this.addContains(parentName, childName)
    }

     addConstraint(allocation1FromName, allocation1ToName, allocation2FromName, allocation2ToName, constraintType) {
        console.log('Adding Constraint from '+allocation1FromName+'->'+allocation1ToName+' to '+allocation2FromName+'->'+allocation2ToName);
        console.log('  constraintType: '+constraintType);
        var a1 = this.getAllocation(allocation1FromName, allocation1ToName);
        var a2 = this.getAllocation(allocation2FromName, allocation2ToName);

        console.log('Allocation1: '+a1);
        console.log('Allocation2: '+a2);

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
            this.resources.forEach(function(res, index) {
                names.push(res.getValue())
            });
         }
         else if (typeName == 'activity') {
            this.activities.forEach(function(act, index) {
                names.push(act.getValue())
            });
         }
         else {
            throw "type name: "+typeName+" is not found in graph (try using 'resource' or 'activity'";
         }

         return names

     }
    
    getAllNamesOfChildrenOf(parentName) {
        var names = [];
        this.containsLinks.forEach(function(link, index) {
            let linkParentName = link.source.getValue();
            let linkChildName = link.target.getValue();
            if (linkParentName == parentName) {
                names.push(linkChildName);
            }
        });
        return names
        
    }

    getAllocation(fromName, toName) {
        console.log("FINDING ALLOCATION: "+fromName+"->"+toName);
        console.log(this.allocatedLinks)
        let allocation = null;
        this.allocatedLinks.forEach(function(link, index) {
            let linkResName = link.source.getValue();
            let linkActName = link.target.getValue();
            console.log("   existingAllocation: "+linkResName+"->"+linkActName);
            if ((linkResName == fromName) && (linkActName == toName)) {
                allocation = link;
            }
        });
        return allocation
    }

    getAllNamesOfAllocatedFrom(resName) {
        var names = [];
        this.allocatedLinks.forEach(function(link, index) {
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
            if (cell.isVertex() && (cell.getParent()==this.graph.getDefaultParent())) {
               nameArray.push(cell.getValue())
            }
        }
        return nameArray.includes(name)
    }

    doesActivityExist(name) {
        let nameArray = [];
        let activity = undefined
        this.activities.forEach(function(act, index) {
           nameArray.push(act.getValue())
        });
        return nameArray.includes(name)
    }

    doesResourceExist(name) {
        let nameArray = []
        this.resources.forEach(function(res, index) {
            nameArray.push(res.getValue())
        });
        return nameArray.includes(name)
    }


 }