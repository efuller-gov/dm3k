function worksheetUtils_helperParagraphTransitionTo(worksheetName){
    let helperTextArr = [
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
            'pane-title-text': 'Continue by creating activities to allocate to resources.',
            'pane-body-text': '<b>Activities</b> are entities that get allocated to <b>resources</b>. When you define an activity, try '+
            'to find a category type that best describes it from the dropdown menu. In our backpack problem, we need to allocate to different backpacks.'+
            'Since we defined backpack as a resource, we will define a new <b>activity</b> to allocate called <b>textbook</b>. It can be best described as an <b>item</b>.',
            'instance-title-text': '',
            'instance-body-text': '',
        },
        {
            'worksheet': 'contains',
            'pane-title-text': 'Create hierarchy within your decision scenario.',
            'pane-body-text': 'A <b>contains</b> relationship creates hierarchy among <b>activities</b> or <b>resources</b> that can be used in allocation logic among instances of activities or resources. '+
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
    ]
    let helperText = helperTextArr.filter(x=>x.worksheet==worksheetName)[0]
    $('#pane-level-explanatory-title').text(helperText['pane-title-text']);
    $('#pane-level-explanatory-text').html(helperText['pane-body-text']);
    $('#instance-level-explanatory-title').hide(); // not sure if there's stuff to include in these yet
    $('#instance-level-explanatory-text').hide();
}
