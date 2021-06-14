<template>
    <div>
    <img src="../assets/dm3k_logo.svg">
    <div id="graphContainer">
    </div>
    </div>
</template>

<script>

  import {Dm3kGraph} from '../js/dm3kgraph/dm3kGraph';

  export default {
    name: 'GraphRenderer',
    data() {
      return {
        dm3kGraph: {}
      }
    },
    mounted() {
        this.loadDm3kGraph();
    },
    watch: {
        '$store.state.resources': {
            deep: true,
            handler(n) {
                // console.log('Resource list changed');
                // console.log(n)
                // console.log(n[n.length-1])
                let latest = n[n.length-1]
                // re render here?
                let newResType = latest.resType
                let newResName = latest.resName
                let newBudgetNameList = latest.newBudgetNameList
                this.dm3kGraph.addCompleteResource(newResType, newResName, newBudgetNameList)
            }
        },
         '$store.state.activities': {
            deep: true,
            handler(activities) {
                console.log('EXISTING ACT TEST: Activity list changed');
                console.log("activities ", activities)
                let latest = activities[activities.length-1]
                console.log("latest act ", latest)
                // re render here?
                let newActType = latest.newActType
                let newActName = latest.actName
                let existingResName = latest.existingResName
                let newRewardName = latest.newRewardName
                let costNum = 1 //REMOVE hardcoded workaround here
                this.dm3kGraph.addCompleteActivity(newActType, newActName, existingResName, newRewardName, costNum)
            }
        }
    },
    methods: {
        loadDm3kGraph() {
            console.log("Initializing graph...")
            this.dm3kGraph = new Dm3kGraph(document.querySelector('#graphContainer'))
        },
    }
  };
</script>

<style scoped>
  .container {
    border-style: groove;
    border-width: thin;
    border-radius: 5px;
    height: 100%;
    width: 100%;
    padding: 5px;
    max-height: 72vh;
    max-width: 100%;
    overflow: hidden;
    border-color: grey;
    margin: 0px;
    transition: border-color 0.2s ease-in-out;
  }

  .container:hover {
    border-color: #242424;
  }

  #graphContainer {
    width: 100%;
    /* height: 100%; */
    margin: 0px;
    padding: 0px;
    min-height: 72vh;
    overflow: hidden;
  }

  .float-tool-bar {
    position: relative;
    top: 0px;
    bottom: 0px;
    right: 0px;
    left: 0px;
    width: 40px;
    height: 200px;
    padding: 0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .tool-btn {
    width: 40px;
    height: 40px;
    border-radius: 999px;
    background: #f5f5f5;
    box-shadow: 0 2px 8px 0 #dcdcdc;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    margin-bottom: 5px;
    pointer-events: auto;
  }

  .menu-btn {
    background: transparent;
    transition: 0ms;
  }

  .overlapContainer {
    position: relative;
    width: 100%;
  }

  .buttonList {
    pointer-events: none;
    padding: 5px 0px 0px 5px;
    list-style-type: none;
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0px;
    bottom: 0px;
    right: 0px;
    left: 0px;
    z-index: 1
  }

  li {
    pointer-events: none;
  }

  .textinfo {
    position: absolute;
    color: #b3b3b3;
    font-size: 14px;
    padding: 10px;
    bottom: 0px;
  }

</style>
