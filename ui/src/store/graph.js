
import Vue from 'vue';
import Vuex from 'vuex';
import {AllocationInstance} from '../js/dm3kgraph/dataClasses';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
      resources : [],
      activities: [],
      allocatedLinks : [],
      containsLinks : [],
      constraints : [],
      resourceInstances : [],
      activityInstances : [],
      containsInstances : [],
      allocatedToInstances : [],
      rewards : {},
      budgets : {},
      costs : {}
},
  getters: {},
  mutations: {
    addResource(state, resourceObj) {
      state.resources.push(resourceObj)
    },
    addResourceInstance(state, resPayload){
      let resName = resPayload['instanceName']
      let resourceInstanceObj = resPayload['newInstance']
      state.resourceInstances.filter(x=>x.label==resName)[0].instanceTableData.push(resourceInstanceObj)
    },
    addActivity(state, activityObj) {
      state.activities.push(activityObj);
      console.log("____addActivity paylod", activityObj)
      // Add AllocationInstance when first create
      let ai = new AllocationInstance(activityObj['existingResName'], activityObj['actName']);
      state.allocatedToInstances.push(ai);
      console.log("__result state.allocatedToInstances ", state.allocatedToInstances)
    },
    addActivityInstance(state, actPayload){
      let actName = actPayload['instanceName']
      let activityInstanceObj = actPayload['newInstance']
      state.activityInstances.filter(x=>x.label==actName)[0].instanceTableData.push(activityInstanceObj)
    },
    addAllocation(state, allocObj) {
      console.log("addAllocation paylod", allocObj)
      state.allocatedLinks.push(allocObj);
      let ai = new AllocationInstance(allocObj['existingResName'], allocObj['actName']);
      state.allocatedToInstances.push(ai);
    },
    addCanBeAllocatedTo(state, allocObj){
      // let ai = new AllocationInstance(allocObj['existingResName'], allocObj['actName']);
      console.log("--> ADD AllocationInstance to..." )
      console.log("allocObj ", allocObj)
      console.log("state.allocatedToInstances ", state.allocatedToInstances)
      state.allocatedToInstances.filter(x=>(x.actName==allocObj['actName'] && x.resName==allocObj['existingResName']))[0].instanceTableData.push(
        { activityInstance: "ALL",
          resourceInstance: "ALL"}
      );
      console.log("--> RESULT state.allocatedToInstances ", state.allocatedToInstances)
    },
    removeResourceInstance(state, resObj){
      console.log("-----> REMOVE RES INSTANCE ", state.resourceInstances.filter(x=>x.label==resObj['name'])[0])
      state.resourceInstances.filter(x=>x.label==resObj['name'])[0]
    }
  },
  actions: {}
});