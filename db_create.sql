pragma foreign_keys = on;

drop table if exists Expense;
drop table if exists Tags;

create table Expense (
    eId         integer     primary key autoincrement,
    date        date        not null,
    amount      float       not null,
    name        text,
    comments    text
);

create table Tag (
    name        text        primary key
);

create table TaggedExpense (
    eId         integer,
    name        text,
    primary key (eId, name),
    foreign key (eId) references Expense (eId) on delete cascade on update cascade,
    foreign key (name) references Tag (name) on delete cascade on update cascade
);

insert into Expense values (null, date('now'), 100.0, 'test one', 'comment one');
insert into Expense values (null, date('now'), 158.3, 'test two', null);
insert into Expense values (4, date('now'), 102, 'test three-four', null);
insert into Tag values ('food');
insert into Tag values ('recurrent');
insert into TaggedExpense values (1, 'food');
insert into TaggedExpense values (1, 'recurrent');
insert into TaggedExpense values (2, 'food');
