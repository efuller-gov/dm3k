
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
    },
    addActivityInstance(state, actPayload){
      let actName = actPayload['instanceName']
      let activityInstanceObj = actPayload['newInstance']
<<<<<<< HEAD
=======
      console.log("-- Within store. Pushing new act inst: ", activityInstanceObj)
>>>>>>> 700db81224dd8330c639219f1d7a537a1c70da7c
      state.activityInstances.filter(x=>x.label==actName)[0].instanceTableData.push(activityInstanceObj)
    },
    addAllocation(state, allocObj) {
      state.allocatedLinks.push(allocObj);
    },
    addCanBeAllocatedTo(state, allocObj){
      let ai = new AllocationInstance(allocObj['existingResName'], allocObj['actName']);
      console.log("--> AllocationInstance", ai)
      state.allocatedToInstances.push(ai);
    }
  },
  actions: {}
});