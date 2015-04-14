var HelloBox = React.createClass({
    getInitialState : function () {
        return {
            greeting: 'Hello world!'
        }
    },
    render: function() {
        return (
            <h1>{this.state.greeting}</h1>
        );
    }
});

React.render(
    <HelloBox />,
    $('.col-md-12').get(0)
);