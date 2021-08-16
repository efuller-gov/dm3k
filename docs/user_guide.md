# Open-DM3K User Guide #

This user guide describes how to use the UI to create/solve resource allocation problems


### **Create resource class**
The first step in defining an allocation problem is to create your *resources*.

Filling out the dropdown and adlib worksheet creates a box representing a resource class.

![](./gifs/res-1.gif)



### **Create resource instances**
You can add additional instances of these resources via the i-button on the resource class box.

Change the names of each instance and the amount of allocated budget.

![](./gifs/res-2.gif)



### **Allocate resources to activities**
After creating resources, you may create activities by allocating your resources.

Once you create at least one resource-activity pair, you will be able to allocate new resources to the same activities, as well as access all subsequent worksheets.

![](./gifs/activity-1.gif)



### **Create activity instances**
Create instances of your activities in the same way as resources.

You may define instance-level allocation relationships by clicking the i-button on the allocation arrow itself and access the drop down menus for each instance.

Default instance-level allocation is ALL to ALL. This means *any* resource instance may be allocated to *any* activity instance.

![](./gifs/activity-2.gif)



### **Make a contains relationship**
A contains relationship is distinct from an allocation relationship. It can only be made between resource and resource or activity and activity.

This type of relationship will impact the Optimal Allocation Plan.

![](./gifs/contains-relationship.gif)



### **Constrain allocations**
A constraint is a relatinoship between allocations themselves. There are three provided types of constraints: IF-THEN, IF-NOT, andd IF-ONLY.

Constraints mean a target allocation can happen conditionally on the source allocation.

![](./gifs/constrain-allocation.gif)



### **Submit diagram to solver**
Once your allocation problem is complete, you can save the configuration to a file on your system.

To submit the problem to the backend solver, click "Submit to DM3K".

A window will pop up showing a visulization of the result- aka the Optimal Allocation Plan.

This visualization includes a guide on how to interpret it. It is also rich in hover information.

![](./gifs/submit.gif)
